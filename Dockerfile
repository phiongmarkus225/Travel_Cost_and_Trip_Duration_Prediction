# Dockerfile untuk Railway.app — FastAPI Backend
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements API
COPY requirements.api.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.api.txt

# Copy source code API
COPY src/api/app.py .

# Copy model artifacts
COPY models/scaler.joblib .
COPY models/target_scaler.joblib .
COPY models/model_ml_best.joblib .
COPY models/model_dl.pth .

# PORT dari Railway env var (Railway otomatis set $PORT)
ENV MODEL_DIR=/app

EXPOSE 8000

# Railway mengeset $PORT secara otomatis, gunakan shell form agar env var terbaca
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
