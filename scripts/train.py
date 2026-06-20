import pandas as pd
import numpy as np
import joblib
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
from xgboost import XGBRegressor
from sqlalchemy import create_engine
import os

# ==========================================
# 1. LOAD DATA (PostgreSQL dengan Fallback CSV)
# ==========================================
DB_USER = "postgres"
DB_PASSWORD = "yourpassword"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "nyc_taxi_db"
TABLE_NAME = "nyc_taxi_trips"

print("Mencoba mengambil data...")
try:
    # Koneksi PostgreSQL
    db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(db_url)
    
    # Mengambil sampel data (misal 500.000 baris) agar training berjalan cepat & efisien
    query = f"SELECT * FROM {TABLE_NAME} ORDER BY RANDOM() LIMIT 500000"
    df = pd.read_sql_query(query, con=engine)
    print(f"Berhasil memuat {len(df):,} baris data dari PostgreSQL.")
except Exception as e:
    print(f"Gagal koneksi ke database: {e}")
    print("Menggunakan data dari file lokal CSV sebagai fallback...")
    
    if os.path.exists("NYC_Taxi_Cleaned_Analysis_Ready.csv"):
        # Jika database gagal, baca CSV dan ambil sampel acak
        df_full = pd.read_csv("NYC_Taxi_Cleaned_Analysis_Ready.csv")
        df = df_full.sample(n=min(500000, len(df_full)), random_state=42).copy()
        del df_full # Hapus dari memori
        print(f"Berhasil memuat {len(df):,} baris data dari CSV lokal.")
    else:
        raise FileNotFoundError("File 'NYC_Taxi_Cleaned_Analysis_Ready.csv' tidak ditemukan.")

# ==========================================
# 2. PREPROCESSING & FEATURE SELECTION
# ==========================================
# Mengisi nilai null Airport fee jika ada
df['Airport_fee'] = df['Airport_fee'].fillna(0)
df['store_and_fwd_flag'] = df['store_and_fwd_flag'].map({'N': 0, 'Y': 1}).fillna(0).astype(int)

# One-hot encoding day_of_week & hour_bucket
df_encode = pd.get_dummies(df, columns=['day_of_week', 'hour_bucket'], drop_first=True, dtype=int)

# Filter Outliers seperti di notebook Anda
df_clean = df_encode[
    (df_encode['total_amount'] > 0) & (df_encode['total_amount'] < 200) &
    (df_encode['duration_min'] > 0) & (df_encode['duration_min'] < 120) &
    (df_encode['trip_distance'] > 0) & (df_encode['trip_distance'] < 50)
].copy()

print(f"Data setelah pembersihan outlier: {len(df_clean):,} baris.")

# Tentukan kolom input (X) dan target (y)
cols_to_drop = [
    'tpep_pickup_datetime', 'tpep_dropoff_datetime',
    'total_amount', 'duration_min', 'speed_mph',
    'fare_amount', 'extra', 'mta_tax', 'tip_amount', 
    'tolls_amount', 'improvement_surcharge', 'congestion_surcharge', 
    'Airport_fee', 'cbd_congestion_fee', 'is_weekend'
]
# Pastikan kolom-kolom drop ada di DataFrame sebelum di-drop
cols_to_drop = [c for c in cols_to_drop if c in df_clean.columns]

X = df_clean.drop(columns=cols_to_drop)
y = df_clean[['total_amount', 'duration_min']]

# Bagi data Train & Test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Kolom numerik kontinu yang butuh scaling
continuous_cols = ['trip_distance', 'passenger_count', 'pickup_hour']
# Cari kolom continuous_cols yang ada di X
continuous_cols = [c for c in continuous_cols if c in X.columns]

# Buat Scaler Fitur & Fit hanya pada X_train
feature_scaler = StandardScaler()
X_train_scaled = X_train.copy()
X_test_scaled = X_test.copy()

X_train_scaled[continuous_cols] = feature_scaler.fit_transform(X_train[continuous_cols])
X_test_scaled[continuous_cols] = feature_scaler.transform(X_test[continuous_cols])

# Simpan Scaler Fitur untuk deployment
joblib.dump(feature_scaler, 'scaler.joblib')
print("Feature Scaler disimpan sebagai 'scaler.joblib'.")

# Buat Scaler Target (Sangat direkomendasikan untuk Deep Learning agar loss stabil)
target_scaler = StandardScaler()
y_train_scaled = target_scaler.fit_transform(y_train)
y_test_scaled = target_scaler.transform(y_test)

# Simpan Scaler Target untuk deployment (inverse transform)
joblib.dump(target_scaler, 'target_scaler.joblib')
print("Target Scaler disimpan sebagai 'target_scaler.joblib'.")

# ==========================================
# 3. MACHINE LEARNING MODEL (XGBoost Multi-Output)
# ==========================================
print("\n--- Pelatihan Model Machine Learning (XGBoost Multi-Output) ---")

# XGBRegressor mendukung multi-output secara langsung ketika target memiliki 2 kolom
ml_model = XGBRegressor(
    n_estimators=100,
    max_depth=8,
    learning_rate=0.195,
    n_jobs=-1,
    random_state=42
)
ml_model.fit(X_train_scaled, y_train)  # y_train tetap dalam satuan asli (tidak di-scale)

# Prediksi
y_pred_ml = ml_model.predict(X_test_scaled)

# Evaluasi ML
mae_amount_ml  = mean_absolute_error(y_test.iloc[:, 0], y_pred_ml[:, 0])
mae_duration_ml = mean_absolute_error(y_test.iloc[:, 1], y_pred_ml[:, 1])
r2_amount_ml   = r2_score(y_test.iloc[:, 0], y_pred_ml[:, 0])
r2_duration_ml  = r2_score(y_test.iloc[:, 1], y_pred_ml[:, 1])

print(f"ML [total_amount]  -> MAE: ${mae_amount_ml:.2f} | R2 Score: {r2_amount_ml:.4f}")
print(f"ML [duration_min]  -> MAE: {mae_duration_ml:.2f} menit | R2 Score: {r2_duration_ml:.4f}")

# Simpan ML Model
joblib.dump(ml_model, 'model_ml_best.joblib')
print("Model ML disimpan sebagai 'model_ml_best.joblib'.")

# ==========================================
# 4. DEEP LEARNING MODEL (PyTorch MLP)
# ==========================================
print("\n--- Pelatihan Model Deep Learning (PyTorch MLP) ---")

# Definisikan Dataset Custom PyTorch
class TaxiDataset(Dataset):
    def __init__(self, X_data, y_data):
        self.X = torch.tensor(X_data.values, dtype=torch.float32)
        self.y = torch.tensor(y_data, dtype=torch.float32)
        
    def __len__(self):
        return len(self.X)
        
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

# Definisikan Arsitektur Neural Network
# Arsitektur: Linear → BatchNorm1d → ReLU → Dropout (blok 1 & 2), lalu Linear → BatchNorm → ReLU → Linear output
class TaxiMLP(nn.Module):
    def __init__(self, input_dim):
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
            nn.Linear(64, 2)              # 11 → Output: [total_amount, duration_min]
        )

    def forward(self, x):
        return self.net(x)

# Setup DataLoaders
train_dataset = TaxiDataset(X_train_scaled, y_train_scaled)
test_dataset = TaxiDataset(X_test_scaled, y_test_scaled)

train_loader = DataLoader(train_dataset, batch_size=256, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=512, shuffle=False)

# Inisialisasi Model, Loss, dan Optimizer
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
input_dim = X_train_scaled.shape[1]
model = TaxiMLP(input_dim).to(device)
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training Loop
epochs = 5
print(f"Melatih model Deep Learning di device: {device} selama {epochs} epochs...")
for epoch in range(epochs):
    model.train()
    running_loss = 0.0
    for X_batch, y_batch in train_loader:
        X_batch, y_batch = X_batch.to(device), y_batch.to(device)
        
        optimizer.zero_grad()
        predictions = model(X_batch)
        loss = criterion(predictions, y_batch)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item() * X_batch.size(0)
        
    epoch_loss = running_loss / len(train_dataset)
    print(f"Epoch {epoch+1}/{epochs} | Loss: {epoch_loss:.4f}")

# Evaluasi DL
model.eval()
y_pred_dl_scaled = []
with torch.no_grad():
    for X_batch, _ in test_loader:
        X_batch = X_batch.to(device)
        preds = model(X_batch)
        y_pred_dl_scaled.append(preds.cpu().numpy())

y_pred_dl_scaled = np.vstack(y_pred_dl_scaled)

# Kembalikan prediksi DL ke satuan asli menggunakan target_scaler
y_pred_dl = target_scaler.inverse_transform(y_pred_dl_scaled)

# Evaluasi DL
mae_amount_dl = mean_absolute_error(y_test.iloc[:, 0], y_pred_dl[:, 0])
mae_duration_dl = mean_absolute_error(y_test.iloc[:, 1], y_pred_dl[:, 1])
r2_amount_dl = r2_score(y_test.iloc[:, 0], y_pred_dl[:, 0])
r2_duration_dl = r2_score(y_test.iloc[:, 1], y_pred_dl[:, 1])

print(f"\nDL [total_amount]  -> MAE: ${mae_amount_dl:.2f} | R2 Score: {r2_amount_dl:.4f}")
print(f"DL [duration_min]  -> MAE: {mae_duration_dl:.2f} menit | R2 Score: {r2_duration_dl:.4f}")

# Simpan Model PyTorch
torch.save(model.state_dict(), 'model_dl.pth')
print("\nModel Deep Learning disimpan sebagai 'model_dl.pth'.")

# Simpan informasi kolom fitur (opsional, untuk referensi)
features_list = list(X.columns)
print(f"\nTotal fitur: {len(features_list)}")
print(f"Nama fitur: {features_list}")
