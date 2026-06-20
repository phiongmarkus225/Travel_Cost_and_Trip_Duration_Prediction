from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import joblib
import os

# Jika env var MODEL_DIR di-set (misal saat di Docker), gunakan itu.
# Jika tidak, fallback ke folder models/ relatif dari root project.
_env_model_dir = os.environ.get("MODEL_DIR")
if _env_model_dir:
    MODELS_DIR = _env_model_dir
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    MODELS_DIR = os.path.join(BASE_DIR, "models")

app = FastAPI(
    title="NYC Taxi Fare & Duration Predictor",
    description="API untuk memprediksi tarif total dan durasi perjalanan taksi NYC menggunakan XGBoost (ML) dan PyTorch MLP (DL).",
    version="2.0"
)

# ==========================================
# DAFTAR FITUR (17 kolom) — harus sama dengan saat training
# ==========================================
FEATURES_LIST = [
    'VendorID', 'passenger_count', 'trip_distance', 'RatecodeID',
    'store_and_fwd_flag', 'PULocationID', 'DOLocationID', 'payment_type',
    'pickup_hour',
    'day_of_week_Monday', 'day_of_week_Saturday', 'day_of_week_Sunday',
    'day_of_week_Thursday', 'day_of_week_Tuesday', 'day_of_week_Wednesday',
    'hour_bucket_Regular', 'hour_bucket_Rush Hour'
]

# Kolom kontinu yang di-scale oleh feature_scaler
CONTINUOUS_COLS = ['trip_distance', 'passenger_count', 'pickup_hour']

# ==========================================
# DEFINISI ARSITEKTUR DL — harus identik dengan saat training
# (Linear → BatchNorm1d → ReLU → Dropout per blok)
# net.0 = Linear(17,256), net.1 = BatchNorm1d(256), net.2 = ReLU, net.3 = Dropout
# net.4 = Linear(256,128), net.5 = BatchNorm1d(128), net.6 = ReLU, net.7 = Dropout
# net.8 = Linear(128,64),  net.9 = BatchNorm1d(64),  net.10= ReLU
# net.11= Linear(64, 2)
# ==========================================
class TaxiMLP(nn.Module):
    def __init__(self, input_dim: int = 17):
        super(TaxiMLP, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),   # 0
            nn.BatchNorm1d(256),          # 1
            nn.ReLU(),                    # 2
            nn.Dropout(0.2),              # 3
            nn.Linear(256, 128),          # 4
            nn.BatchNorm1d(128),          # 5
            nn.ReLU(),                    # 6
            nn.Dropout(0.2),              # 7
            nn.Linear(128, 64),           # 8
            nn.BatchNorm1d(64),           # 9
            nn.ReLU(),                    # 10
            nn.Linear(64, 2)              # 11  → [total_amount, duration_min]
        )

    def forward(self, x):
        return self.net(x)


# ==========================================
# LOAD MODEL & SCALERS
# ==========================================
try:
    # Scaler fitur & target
    feature_scaler = joblib.load(os.path.join(MODELS_DIR, 'scaler.joblib'))
    target_scaler  = joblib.load(os.path.join(MODELS_DIR, 'target_scaler.joblib'))

    # ML Model: XGBoost multi-output regressor
    ml_model = joblib.load(os.path.join(MODELS_DIR, 'model_ml_best.joblib'))

    # DL Model: PyTorch MLP dengan BatchNorm
    dl_model = TaxiMLP(input_dim=len(FEATURES_LIST))
    dl_model.load_state_dict(
        torch.load(os.path.join(MODELS_DIR, 'model_dl.pth'), map_location=torch.device('cpu'), weights_only=False)
    )
    dl_model.eval()

    print("Semua model dan scaler berhasil dimuat.")
    print(f"  - ML Model : {type(ml_model).__name__}")
    print(f"  - DL Model : TaxiMLP (input_dim={len(FEATURES_LIST)})")

except Exception as e:
    print(f"Warning: Gagal memuat file model/scaler: {e}")
    print("Pastikan 'train.py' sudah dijalankan dan semua file .joblib / .pth ada.")
    ml_model = None
    dl_model  = None


# ==========================================
# INPUT SCHEMA
# ==========================================
class RideInput(BaseModel):
    VendorID: int
    passenger_count: float
    trip_distance: float
    RatecodeID: float
    store_and_fwd_flag: str   # 'N' atau 'Y'
    PULocationID: int
    DOLocationID: int
    payment_type: int
    pickup_hour: int
    day_of_week: str          # 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    hour_bucket: str          # 'Late Night', 'Regular', 'Rush Hour'


# ==========================================
# HELPER: build & preprocess DataFrame
# ==========================================
def _preprocess(data: RideInput) -> pd.DataFrame:
    """Konversi input → DataFrame berfitur 17, sudah di-scale."""
    raw = {
        'VendorID':          [data.VendorID],
        'passenger_count':   [data.passenger_count],
        'trip_distance':     [data.trip_distance],
        'RatecodeID':        [data.RatecodeID],
        'store_and_fwd_flag':[1 if data.store_and_fwd_flag == 'Y' else 0],
        'PULocationID':      [data.PULocationID],
        'DOLocationID':      [data.DOLocationID],
        'payment_type':      [data.payment_type],
        'pickup_hour':       [data.pickup_hour],
        'day_of_week':       [data.day_of_week],
        'hour_bucket':       [data.hour_bucket],
    }
    df = pd.DataFrame(raw)

    # One-hot encode day_of_week & hour_bucket (drop_first=True, sama seperti training)
    df_enc = pd.get_dummies(df, columns=['day_of_week', 'hour_bucket'], drop_first=True, dtype=int)

    # Selaraskan kolom dengan training (isi kolom yang hilang dengan 0)
    df_final = df_enc.reindex(columns=FEATURES_LIST, fill_value=0)

    # Scale kolom kontinu
    cont = [c for c in CONTINUOUS_COLS if c in df_final.columns]
    df_final[cont] = feature_scaler.transform(df_final[cont])

    return df_final


# ==========================================
# ENDPOINTS
# ==========================================
@app.get("/")
def home():
    return {
        "status": "Online",
        "models": {
            "ml": "XGBoost Multi-Output Regressor",
            "dl": "PyTorch MLP with BatchNorm"
        }
    }


@app.post("/predict/ml")
def predict_ml(data: RideInput):
    """Prediksi menggunakan XGBoost (ML model terbaik)."""
    if ml_model is None:
        raise HTTPException(status_code=503, detail="ML model belum terinisialisasi.")

    try:
        df_final = _preprocess(data)

        # XGBRegressor.predict() langsung mengembalikan array (n_samples, 2)
        pred = ml_model.predict(df_final)[0]   # [total_amount, duration_min]

        return {
            "model": "XGBoost",
            "predicted_total_amount":    round(float(max(0.0, pred[0])), 2),
            "predicted_duration_minutes": round(float(max(0.0, pred[1])), 2),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal memproses data: {str(e)}")


@app.post("/predict/dl")
def predict_dl(data: RideInput):
    """Prediksi menggunakan PyTorch MLP (DL model)."""
    if dl_model is None:
        raise HTTPException(status_code=503, detail="DL model belum terinisialisasi.")

    try:
        df_final = _preprocess(data)

        input_tensor = torch.tensor(df_final.values, dtype=torch.float32)
        with torch.no_grad():
            pred_scaled = dl_model(input_tensor).numpy()

        # Inverse transform target scaler → satuan asli
        pred_original = target_scaler.inverse_transform(pred_scaled)[0]

        return {
            "model": "PyTorch MLP (BatchNorm)",
            "predicted_total_amount":    round(float(max(0.0, pred_original[0])), 2),
            "predicted_duration_minutes": round(float(max(0.0, pred_original[1])), 2),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal memproses data: {str(e)}")


@app.post("/predict")
def predict(data: RideInput):
    """Prediksi dari kedua model sekaligus (ML + DL)."""
    if ml_model is None or dl_model is None:
        raise HTTPException(status_code=503, detail="Salah satu atau kedua model belum terinisialisasi.")

    try:
        df_final = _preprocess(data)

        # --- ML ---
        pred_ml = ml_model.predict(df_final)[0]

        # --- DL ---
        input_tensor = torch.tensor(df_final.values, dtype=torch.float32)
        with torch.no_grad():
            pred_dl_scaled = dl_model(input_tensor).numpy()
        pred_dl = target_scaler.inverse_transform(pred_dl_scaled)[0]

        return {
            "ml_model": {
                "name": "XGBoost",
                "predicted_total_amount":    round(float(max(0.0, pred_ml[0])), 2),
                "predicted_duration_minutes": round(float(max(0.0, pred_ml[1])), 2),
            },
            "dl_model": {
                "name": "PyTorch MLP (BatchNorm)",
                "predicted_total_amount":    round(float(max(0.0, pred_dl[0])), 2),
                "predicted_duration_minutes": round(float(max(0.0, pred_dl[1])), 2),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal memproses data: {str(e)}")
