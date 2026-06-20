import pandas as pd
from sqlalchemy import create_engine
import time

# Konfigurasi Koneksi PostgreSQL
# Ganti username, password, host, port, dan db_name sesuai konfigurasi PostgreSQL Anda
DB_USER = "postgres"
DB_PASSWORD = "admin123"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "nyc_taxi_db"
TABLE_NAME = "nyc_taxi_trips"

# Membuat Engine Koneksi Database
db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(db_url)

csv_file_path = "NYC_Taxi_Cleaned_Analysis_Ready.csv"
chunk_size = 100000  # Unggah per 100.000 baris agar hemat memori (RAM)

print("Memulai proses unggah data ke PostgreSQL...")
start_time = time.time()

# Iterasi membaca CSV per-chunk dan mengunggahnya ke PostgreSQL
first_chunk = True
for i, chunk in enumerate(pd.read_csv(csv_file_path, chunksize=chunk_size)):
    chunk_start_time = time.time()
    
    # Isi nilai null pada Airport_fee sebelum unggah
    if 'Airport_fee' in chunk.columns:
        chunk['Airport_fee'] = chunk['Airport_fee'].fillna(0)
        
    # Ubah tipe data tanggal
    chunk['tpep_pickup_datetime'] = pd.to_datetime(chunk['tpep_pickup_datetime'])
    chunk['tpep_dropoff_datetime'] = pd.to_datetime(chunk['tpep_dropoff_datetime'])
    chunk['is_weekend'] = chunk['is_weekend'].astype(int)
    
    # Simpan ke PostgreSQL
    # 'replace' untuk chunk pertama agar tabel di-reset, 'append' untuk chunk berikutnya
    if first_chunk:
        chunk.to_sql(TABLE_NAME, con=engine, if_exists='replace', index=False)
        first_chunk = False
    else:
        chunk.to_sql(TABLE_NAME, con=engine, if_exists='append', index=False)
        
    chunk_end_time = time.time()
    print(f"Chunk {i+1} ({len(chunk):,} baris) terunggah dalam {chunk_end_time - chunk_start_time:.2f} detik.")

end_time = time.time()
print(f"\nSelesai! Seluruh data berhasil dimasukkan ke tabel '{TABLE_NAME}' dalam {end_time - start_time:.2f} detik.")
