# Rencana Implementasi Preprocessing, Modeling, PostgreSQL, dan Docker

Dokumen ini diperbarui untuk mengakomodasi kebutuhan tambahan Anda:
1. Konfirmasi target prediksi: Estimasi harga (`total_amount`) dan durasi perjalanan (`duration_min`) menggunakan **Multi-Output Regression**.
2. Penyimpanan dan pembacaan dataset melalui **PostgreSQL**.
3. Containerization aplikasi deployment menggunakan **Docker**.

---

## User Review Required

> [!IMPORTANT]
> **Integrasi PostgreSQL:** Kita akan menuliskan kode Python menggunakan library `sqlalchemy` dan `psycopg2` untuk memindahkan data dari file CSV (`NYC_Taxi_Cleaned_Analysis_Ready.csv`) ke tabel PostgreSQL, serta bagaimana membacanya kembali ke pandas untuk training.
> *Anda perlu memastikan database PostgreSQL Anda berjalan dan memiliki kredensial yang sesuai.*

> [!IMPORTANT]
> **Dockerization:** Kami akan membuat:
> 1. `Dockerfile` untuk membungkus aplikasi web API (FastAPI) yang menjalankan model Deep Learning PyTorch.
> 2. `docker-compose.yml` untuk mempermudah menjalankan container aplikasi secara lokal, yang dapat dihubungkan ke PostgreSQL jika diperlukan.

---

## Proposed Changes

Rangkaian langkah kerja diatur kembali menjadi komponen berikut:

### 1. Ingestion & Database (PostgreSQL)
- Menulis script python (`db_ingest.py`) untuk:
  - Membuat koneksi ke database PostgreSQL menggunakan `sqlalchemy`.
  - Mengunggah data bersih ke tabel bernama `nyc_taxi_trips` menggunakan `.to_sql()`.
- Menunjukkan cara query data dari PostgreSQL langsung ke Pandas DataFrame untuk keperluan training.

### 2. Preprocessing & Feature Scaling
- Memisahkan fitur `X` dan target multi-output `y = ['total_amount', 'duration_min']`.
- Menerapkan `StandardScaler` pada fitur numerik kontinu dan menyimpan objek scaler sebagai `scaler.joblib`.

### 3. Machine Learning Baseline
- Melatih model regresi linear/Ridge multi-output sebagai benchmark.
- Menampilkan metrik **$R^2$ Score** (representasi akurasi) dan **MAE** (selisih rata-rata).

### 4. Deep Learning Model (PyTorch)
- Membuat Neural Network Multi-Output Regresi dengan input dari scaler dan output berdimensi 2 (`total_amount`, `duration_min`).
- Melatih model dengan PyTorch DataLoader (menggunakan data sampling demi efisiensi memori).
- Menyimpan model terlatih sebagai `model_dl.pth`.

### 5. Deployment Web API (FastAPI & Docker)
- Membuat aplikasi FastAPI sederhana (`app.py`) dengan endpoint `/predict` yang:
  - Menerima JSON payload data perjalanan baru.
  - Memproses input dengan `scaler.joblib`.
  - Menghasilkan prediksi harga dan durasi dengan `model_dl.pth`.
- Membuat `Dockerfile` berbasis Python ringan untuk membungkus aplikasi.
- Membuat `docker-compose.yml` untuk menyatukan dan menjalankan aplikasi dengan sekali perintah `docker compose up`.

---

## Verification Plan

### Automated Tests
- Menjalankan uji coba koneksi ke PostgreSQL menggunakan potongan script.
- Melakukan verifikasi build Docker image secara lokal.

### Manual Verification
- Mengirimkan request POST (menggunakan `curl` atau browser) ke endpoint `/predict` di dalam container Docker dan memastikan response JSON mengembalikan nilai prediksi `total_amount` dan `duration_min` yang valid.
