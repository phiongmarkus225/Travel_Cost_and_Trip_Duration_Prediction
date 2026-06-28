# 🚕 NYC Taxi Fare & Duration Predictor

Proyek ini adalah sistem prediksi multi-output komprehensif untuk mengestimasi **Tarif Total (`total_amount`)** dan **Durasi Perjalanan (`duration_min`)** taksi New York City (NYC). Proyek ini menggabungkan integrasi database PostgreSQL, pelatihan model Machine Learning (XGBoost) dan Deep Learning (PyTorch MLP), penyajian API menggunakan FastAPI, serta antarmuka visual interaktif berbasis Streamlit. 

---

## 📂 Struktur Proyek

```directory
Take_Home_Test/
├── .streamlit/
│   └── secrets.toml            # Konfigurasi rahasia Streamlit Cloud (API URL)
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
├── Dockerfile                  # Dockerfile untuk deploy FastAPI ke Railway.app
├── docker-compose.yml          # Konfigurasi orkestrasi container Docker
├── requirements.api.txt        # Dependensi khusus API (FastAPI & Models)
├── requirements.frontend.txt   # Dependensi khusus Streamlit
├── requirements.txt            # Dependensi gabungan/utama proyek
└── README.md                   # Dokumentasi proyek (file ini)
```

---

## 🚀 Cara Menjalankan Proyek

Terdapat tiga cara untuk menjalankan proyek ini: menggunakan **Docker Compose** (lokal), **Lokal (Manual)**, atau **Production Deployment (Cloud)**.

### Metode A: Menggunakan Docker Compose (Lokal)

Docker akan mengorkestrasi tiga layanan (Database, API, Frontend) secara otomatis.

1. **Jalankan Container Docker**
   ```bash
   docker compose up --build
   ```
2. **Akses Layanan**
   * **API Backend (FastAPI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
   * **Frontend Dashboard (Streamlit)**: [http://localhost:8501](http://localhost:8501)

---

### Metode B: Menjalankan Secara Lokal (Manual)

1. **Setup Virtual Environment & Install Dependensi**
   ```bash
   python -m venv venv
   venv\Scripts\activate # Windows
   pip install -r requirements.txt
   ```
2. **Latih Model (Training)**
   ```bash
   python scripts/train.py
   ```
   *Pastikan file `.joblib` & `.pth` dipindahkan ke folder `models/` setelah training.*
3. **Jalankan API Backend & Streamlit**
   * Terminal 1: `uvicorn src.api.app:app --reload --port 8000`
   * Terminal 2: `streamlit run src/frontend/app_streamlit.py`

---

### Metode C: Cloud Deployment (Production)

Proyek ini telah dikonfigurasi untuk dipisah dideployments-nya:
* **Backend API** di-deploy ke **Railway.app** menggunakan `Dockerfile` root.
* **Frontend Streamlit** di-deploy ke **Streamlit Cloud** menggunakan `requirements.txt` yang sangat ramping agar build super cepat tanpa compile source code (tidak butuh Torch/Pandas di frontend).

#### Langkah Konfigurasi Streamlit Cloud:
1. Deploy repositori ke Streamlit Cloud dengan main module `src/frontend/app_streamlit.py`.
2. Pada pengaturan aplikasi di Streamlit Cloud, buka **Secrets** dan tambahkan URL API backend Railway Anda:
   ```toml
   API_URL = "https://nama-aplikasi-anda.up.railway.app"
   ```

---

## 💡 Fitur Terbaru Frontend Streamlit

1. **Peta Zone Dropdown Interaktif**: Input lokasi pickup dan dropoff tidak lagi berupa angka ID yang membingungkan. Sekarang menggunakan dropdown nama zona resmi NYC TLC (265 zona lengkap) yang dapat dicari (searchable).
2. **Auto-Calculate Jarak (Opsi B)**: Jarak perjalanan (`trip_distance`) dihitung secara otomatis menggunakan formula **Haversine** (jarak garis lurus) dari koordinat centroid zona pickup ke dropoff, kemudian dikalikan dengan faktor koreksi jalan raya perkotaan (**1.35x**).
3. **Manual Override**: Pengguna tetap dapat mengubah estimasi jarak otomatis tersebut secara manual jika mengetahui rute jalan pintas/alternatif yang lebih spesifik.

---

## 🔌 Detail API Endpoints (FastAPI)

* **`GET /`**: Mengembalikan status kesehatan API.
* **`POST /predict`**: Mengembalikan hasil estimasi rute dari **XGBoost (ML)** dan **PyTorch MLP (DL)** sekaligus untuk perbandingan.
* **`POST /predict/ml`**: Prediksi khusus menggunakan model **XGBoost**.
* **`POST /predict/dl`**: Prediksi khusus menggunakan model **PyTorch MLP**.

---

## 🧠 Detail Pemodelan

1. **XGBoost Multi-Output Regressor**
   * Sangat optimal untuk dataset terstruktur. Memprediksi tarif total dan durasi sekaligus.
2. **PyTorch Multi-Layer Perceptron (MLP)**
   * Menggunakan arsitektur Deep Learning dengan layer `Linear -> BatchNorm1d -> ReLU -> Dropout` untuk stabilitas training.
