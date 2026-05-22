# Aplikasi Web Pertanian

Aplikasi sederhana dengan Flask dan TensorFlow untuk memilih dan memantau tanaman cabai, tomat, dan terong.

## Fitur
- Pilih tanaman: cabai, tomat, terong
- Tambah data perkembangan tanaman per minggu
- Simpan riwayat perkembangan mingguan
- Prediksi tahap pertumbuhan menggunakan TensorFlow

## Penggunaan
1. Buat virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Latih model AI menggunakan dataset CSV:
   ```bash
   python models\growth_model.py
   ```
4. Jalankan aplikasi:
   ```bash
   python app.py
   ```
5. Buka browser di `http://127.0.0.1:5000`
