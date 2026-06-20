# Gunakan base image python resmi yang ringan
FROM python:3.10-slim

# Tentukan direktori kerja di dalam container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Salin requirements API
COPY requirements.api.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.api.txt

# Salin source code API
COPY src/api/app.py .

# Salin model artifacts
COPY models/scaler.joblib .
COPY models/target_scaler.joblib .
COPY models/model_ml_best.joblib .
COPY models/model_dl.pth .

# Port yang diekspos oleh FastAPI
EXPOSE 8000

# Override BASE_DIR agar app.py mencari model di /app saat dalam container
ENV MODEL_DIR=/app

# Jalankan server uvicorn saat container dimulai
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
