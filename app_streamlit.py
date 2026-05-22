import streamlit as st
import json
import os
from models.growth_model import (
    predict_growth_stage, 
    predict_harvest_days, 
    evaluate_plant_condition, 
    generate_care_recommendations, 
    compute_health_score
)

# Konfigurasi halaman
st.set_page_config(page_title="Agro Plant Tracker", page_icon="🌿", layout="wide")

DATA_FILE = os.path.join(os.getcwd(), 'data', 'weekly_data.json')

PLANTS = {
    'cabai': {
        'label': 'Cabai',
        'description': 'Tanaman cabai membutuhkan sinar matahari penuh, tanah gembur, dan penyiraman teratur.'
    },
    'tomat': {
        'label': 'Tomat',
        'description': 'Tomat tumbuh baik pada suhu hangat dan kelembapan seimbang dengan pemupukan rutin.'
    },
    'terong': {
        'label': 'Terong',
        'description': 'Terong membutuhkan paparan sinar matahari setidaknya 6 jam per hari dan drainase yang baik.'
    }
}

def load_data():
    if not os.path.exists(DATA_FILE):
        return {plant: [] for plant in PLANTS}
    with open(DATA_FILE, 'r', encoding='utf-8') as data_file:
        return json.load(data_file)

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as data_file:
        json.dump(data, data_file, ensure_ascii=False, indent=2)

# ================= UI STREAMLIT =================

st.title("🌿 Agro Plant Tracker & AI Analysis")

# Pemicu Notifikasi Sukses via Session State (Solusi Bug No Refres)
if "success_msg" in st.session_state:
    st.success(st.session_state.success_msg)
    del st.session_state.success_msg

data = load_data()

# SIDEBAR: Pilih Tanaman
st.sidebar.header("Pilih Menu")
plant_choice = st.sidebar.selectbox(
    "Jenis Tanaman:", 
    list(PLANTS.keys()), 
    format_func=lambda x: PLANTS[x]['label']
)

plant_info = PLANTS[plant_choice]
st.header(f"Memantau: {plant_info['label']}")
st.write(plant_info['description'])

# TABS: Memisahkan tampilan biar rapi mirip routing di Flask
tab1, tab2, tab3 = st.tabs(["📊 Dashboard & Prediksi", "📝 Input Data Baru", "📄 Riwayat Laporan"])

records = data.get(plant_choice, [])

# --- TAB 1: DASHBOARD & HASIL AI ---
with tab1:
    if not records:
        st.info(f"Belum ada data untuk {plant_info['label']}. Silakan input data di tab 'Input Data Baru'.")
    else:
        last = records[-1]
        
        st.subheader("Data Pengukuran Terakhir")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Umur (Hari)", last.get('age_days', 0))
        col2.metric("Tinggi (cm)", last.get('height_cm', 0))
        col3.metric("Jumlah Daun", last.get('leaf_count', 0))
        col4.metric("Suhu (°C)", last.get('temperature_c', 0))

        # Proses Kalkulasi Model
        health_score = compute_health_score(
            float(last.get('age_days', 0)),
            float(last.get('height_cm', 0)),
            int(last.get('leaf_count', 0)),
            float(last.get('temperature_c', 0)),
            float(last.get('humidity_pct', 0)),
        )
        prediction = predict_growth_stage(
            float(last.get('height_cm', 0)),
            int(last.get('leaf_count', 0)),
            health_score,
        )
        plant_condition = evaluate_plant_condition(
            float(last.get('age_days', 0)),
            float(last.get('temperature_c', 0)),
            float(last.get('humidity_pct', 0)),
        )
        care_recommendations = generate_care_recommendations(
            plant_condition,
            float(last.get('temperature_c', 0)),
            float(last.get('humidity_pct', 0)),
            float(last.get('age_days', 0)),
        )
        
        try:
            raw_estimate = predict_harvest_days(
                float(last.get('age_days', 0)),
                float(last.get('height_cm', 0)),
                int(last.get('leaf_count', 0)),
                float(last.get('humidity_pct', 0)),
                float(last.get('temperature_c', 0)),
                plant_condition,
                plant_choice,
            )
            
            estimasi_hari = int(round(float(raw_estimate)))
            
            if estimasi_hari <= 0:
                harvest_estimate = "Sudah siap panen! 🌾"
            else:
                harvest_estimate = f"Sekitar {estimasi_hari} hari lagi"
                
        except Exception:
            harvest_estimate = "Data belum cukup untuk estimasi."

        st.divider()
        st.subheader("🤖 Analisis AI")
        st.success(f"**Fase Pertumbuhan:** {prediction}")
        st.info(f"**Kondisi Tanaman:** {plant_condition}")
        st.warning(f"**Estimasi Panen:** {harvest_estimate}")
        
        st.subheader("💡 Rekomendasi Perawatan")
        
        if isinstance(care_recommendations, dict):
            for category, tips in care_recommendations.items():
                if category == "watering":
                    st.markdown("💧 **Panduan Penyiraman:**")
                elif category == "fertilizer":
                    st.markdown("🌱 **Panduan Pemupukan:**")
                elif category == "special_actions":
                    st.markdown("⚠️ **Tindakan Khusus:**")
                else:
                    st.markdown(f"📌 **{category.title()}:**")
                
                if isinstance(tips, dict):
                    tips_list = list(tips.values())
                elif isinstance(tips, list):
                    tips_list = tips
                else:
                    tips_list = [tips]
                
                for tip in tips_list:
                    st.markdown(f"- {tip}")
                st.write("") 
                
        elif isinstance(care_recommendations, str):
            try:
                care_dict = json.loads(care_recommendations)
                for category, tips in care_dict.items():
                    st.markdown(f"**{category.title()}:**")
                    if isinstance(tips, dict):
                        tips_list = list(tips.values())
                    elif isinstance(tips, list):
                        tips_list = tips
                    else:
                        tips_list = [tips]
                        
                    for tip in tips_list:
                        st.markdown(f"- {tip}")
                    st.write("")
            except:
                st.write(care_recommendations)
        else:
            st.write(care_recommendations)

# --- TAB 2: FORM INPUT DATA (Fix Reset Bug & Notifikasi) ---
with tab2:
    st.subheader("Input Pertumbuhan Mingguan")
    # clear_on_submit=True otomatis membersihkan form setelah disubmit
    with st.form("input_form", clear_on_submit=True):
        week = st.text_input("Minggu Ke- (Contoh: Minggu 1)")
        age_days = st.number_input("Umur (Hari)", min_value=0)
        height_cm = st.number_input("Tinggi (cm)", min_value=0.0, step=0.1)
        leaf_count = st.number_input("Jumlah Daun", min_value=0)
        humidity_pct = st.number_input("Kelembapan (%)", min_value=0.0, max_value=100.0, step=0.1)
        temperature_c = st.number_input("Suhu (°C)", min_value=0.0, step=0.1)
        
        submitted = st.form_submit_button("Simpan Data")
        
        if submitted:
            if not week.strip():
                st.error("Kolom 'Minggu Ke-' wajib diisi bro!")
            else:
                record = {
                    'week': week.strip(),
                    'age_days': int(age_days),
                    'height_cm': float(height_cm),
                    'leaf_count': int(leaf_count),
                    'humidity_pct': float(humidity_pct),
                    'temperature_c': float(temperature_c),
                }
                data.setdefault(plant_choice, []).append(record)
                save_data(data)
                
                # Masukkan notifikasi ke session_state sebelum halaman di-refresh secara paksa
                st.session_state.success_msg = f"🎉 Data untuk '{week.strip()}' berhasil disimpan!"
                st.rerun()

# --- TAB 3: REPORT/RIWAYAT & FITUR HAPUS DATA ---
with tab3:
    st.subheader(f"Riwayat Data {plant_info['label']}")
    if records:
        # Menampilkan tabel data utama
        st.dataframe(records, use_container_width=True)
        
        # Penambahan Fitur Hapus Data Terpilih
        st.divider()
        st.subheader("🗑️ Hapus Riwayat Pengukuran")
        
        # Menyusun opsi pilihan drop-down dengan menyisipkan Index list array-nya
        options_to_delete = [f"Data Ke-{idx+1}: {r.get('week')} (Umur {r.get('age_days')} hari)" for idx, r in enumerate(records)]
        selected_data = st.selectbox("Pilih baris data yang ingin dihapus:", options_to_delete, index=None, placeholder="Pilih data...")
        
        confirm_delete = st.button("Hapus Data Terpilih", type="primary")
        
        if confirm_delete:
            if selected_data:
                # Cari tau posisi index keberapa data tersebut berada di file JSON
                idx_to_delete = options_to_delete.index(selected_data)
                removed_record = data[plant_choice].pop(idx_to_delete)
                save_data(data) # Simpan ulang perubahan JSON
                
                # Kirim sinyal sukses
                st.session_state.success_msg = f"🗑️ Data '{removed_record.get('week')}' telah berhasil dihapus permanen!"
                st.rerun()
            else:
                st.warning("Pilih salah satu baris data terlebih dahulu lewat menu dropdown di atas.")
    else:
        st.write("Belum ada riwayat data.")