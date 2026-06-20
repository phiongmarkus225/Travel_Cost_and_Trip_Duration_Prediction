# 🚕 NYC Taxi Fare & Duration Predictor

Proyek ini adalah sistem prediksi multi-output komprehensif untuk mengestimasi **Tarif Total (`total_amount`)** dan **Durasi Perjalanan (`duration_min`)** taksi New York City (NYC). Proyek ini menggabungkan integrasi database PostgreSQL, pelatihan model Machine Learning (XGBoost) dan Deep Learning (PyTorch MLP), penyajian API menggunakan FastAPI, serta antarmuka visual interaktif berbasis Streamlit. Seluruh arsitektur dikontainerisasi menggunakan Docker.

---

## 📂 Struktur Proyek

```directory
Take_Home_Test/
├── data/                       # Tempat penyimpanan dataset CSV (diabaikan oleh Git)
├── docker/                     # Berisi konfigurasi Dockerfile
│   ├── Dockerfile              # Dockerfile untuk API (FastAPI)
│   └── Dockerfile.streamlit    # Dockerfile untuk Frontend (Streamlit)
├── models/                     # Tempat penyimpanan model & scaler hasil training (.joblib, .pth)
├── notebooks/                  # Jupyter Notebooks untuk analisis eksploratif
├── scripts/                    # Scripts untuk ingestion dan training model
│   ├── db_ingest.py            # Ingest data CSV ke database PostgreSQL
│   └── train.py                # Pelatihan model XGBoost dan PyTorch MLP
├── src/                        # Source code aplikasi
│   ├── api/
│   │   └── app.py              # API backend FastAPI
│   └── frontend/
│       └── app_streamlit.py    # Dashboard frontend Streamlit
├── docker-compose.yml          # Konfigurasi orkestrasi container Docker
├── requirements.txt            # Dependensi utama proyek
└── README.md                   # Dokumentasi proyek (file ini)
```

---

## 🚀 Cara Menjalankan Proyek

Terdapat dua cara untuk menjalankan proyek ini: menggunakan **Docker Compose** (direkomendasikan) atau menjalankannya secara **Lokal (Manual)**.

### Kebutuhan Awal (Prerequisites)
Pastikan Anda telah mengunduh dataset `NYC_Taxi_Cleaned_Analysis_Ready.csv` dan meletakkannya di direktori utama (root) proyek sebelum memulai.

---

### Metode A: Menggunakan Docker Compose (Direkomendasikan)

Dengan Docker Compose, Anda tidak perlu menginstal Python, PostgreSQL, atau library pendukung lainnya di komputer lokal Anda. Docker akan mengorkestrasi tiga layanan (Database, API, Frontend) secara otomatis.

1. **Jalankan Container Docker**
   Buka terminal di direktori proyek dan jalankan perintah berikut:
   ```bash
   docker compose up --build
   ```

2. **Akses Layanan**
   Setelah semua container berjalan:
   * **API Backend (FastAPI)**: Akses dokumentasi interaktif Swagger API di [http://localhost:8000/docs](http://localhost:8000/docs).
   * **Frontend Dashboard (Streamlit)**: Buka browser dan akses [http://localhost:8501](http://localhost:8501).
   * **Database (PostgreSQL)**: Berjalan di `localhost:5432` dengan user `postgres` dan database `nyc_taxi_db`.

---

### Metode B: Menjalankan Secara Lokal (Manual)

Jika Anda ingin menjalankan proyek di luar Docker (misalnya untuk development atau debugging):

1. **Setup Virtual Environment & Install Dependensi**
   ```bash
   # Membuat virtual environment
   python -m venv venv
   
   # Aktivasi virtual environment (Windows)
   venv\Scripts\activate
   
   # Instalasi dependensi
   pip install -r requirements.txt
   ```

2. **Ingest Data ke PostgreSQL (Opsional)**
   Pastikan Anda memiliki database PostgreSQL lokal yang sedang berjalan, kemudian sesuaikan kredensial di [scripts/db_ingest.py](file:///c:/Users/user/Downloads/Take_Home_Test/scripts/db_ingest.py) dan jalankan:
   ```bash
   python scripts/db_ingest.py
   ```

3. **Latih Model (Training)**
   Script training akan memuat data dari PostgreSQL (atau fallback ke CSV lokal jika database tidak terjangkau) untuk melatih model XGBoost dan PyTorch MLP:
   ```bash
   python scripts/train.py
   ```
   Setelah selesai, file model (`model_ml_best.joblib`, `model_dl.pth`) dan scaler (`scaler.joblib`, `target_scaler.joblib`) akan tersimpan di direktori utama. Pindahkan/salin file-file tersebut ke folder `models/` agar terbaca oleh API.

4. **Jalankan API Backend (FastAPI)**
   ```bash
   uvicorn src.api.app:app --reload --port 8000
   ```

5. **Jalankan Frontend (Streamlit)**
   Buka terminal baru (pastikan venv aktif) dan jalankan:
   ```bash
   streamlit run src/frontend/app_streamlit.py
   ```

---

## 🔌 Detail API Endpoints (FastAPI)

Aplikasi backend mengekspos beberapa endpoint utama untuk menerima input perjalanan dan mengembalikan estimasi:

* **`GET /`**
  Mengembalikan status kesehatan API beserta jenis model yang digunakan.
  
* **`POST /predict`**
  Menerima detail perjalanan baru dan mengembalikan hasil prediksi dari **XGBoost (ML)** dan **PyTorch MLP (DL)** sekaligus untuk perbandingan.
  
* **`POST /predict/ml`**
  Hanya mengembalikan prediksi menggunakan model **XGBoost**.
  
* **`POST /predict/dl`**
  Hanya mengembalikan prediksi menggunakan model **PyTorch MLP**.

### Contoh Payload Input (JSON)
Kirimkan payload dengan skema seperti berikut ke endpoint `/predict`:
```json
{
  "VendorID": 2,
  "passenger_count": 1.0,
  "trip_distance": 5.4,
  "RatecodeID": 1.0,
  "store_and_fwd_flag": "N",
  "PULocationID": 132,
  "DOLocationID": 230,
  "payment_type": 1,
  "pickup_hour": 14,
  "day_of_week": "Monday",
  "hour_bucket": "Regular"
}
```

---

## 🧠 Detail Pemodelan

Aplikasi ini menggunakan pendekatan **Multi-Output Regression** karena memprediksi dua variabel target numerik secara simultan:

1. **XGBoost Multi-Output Regressor**
   * Model berbasis pohon keputusan (gradient boosting) yang sangat optimal untuk dataset tabular terstruktur.
   * Dilatih langsung dengan target satuan asli.

2. **PyTorch Multi-Layer Perceptron (MLP)**
   * Menggunakan arsitektur Deep Learning: `Linear -> BatchNorm1d -> ReLU -> Dropout` di setiap layer tersembunyi untuk stabilitas pelatihan dan menghindari overfitting.
   * Target dinormalisasi menggunakan `target_scaler.joblib` selama training dan dide-normalisasi kembali (inverse transform) saat inferensi/prediksi.
