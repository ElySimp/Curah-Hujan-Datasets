# ===== KONFIGURASI DAN SETUP =====
import pandas as pd
import mysql.connector
from datetime import datetime
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

# ===== KONEKSI DATABASE =====
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'port': int(os.getenv('MYSQL_PORT'))
}

# ===== DATA STASIUN =====
stasiun_info = {
    'Bogor-Kabupaten': {'nama_stasiun': 'Stasiun Meteorologi Citeko', 'id_wmo': '96751', 'lintang': -670000, 'bujur': 10685000, 'elevasi': 920},
    'Cirebon-Kabupaten': {'nama_stasiun': 'Stasiun Klimatologi Jayapura', 'id_wmo': '97692', 'lintang': -259231, 'bujur': 14016792, 'elevasi': 70},
    'Majalengka-Kabupaten': {'nama_stasiun': 'Stasiun Meteorologi Kertajati', 'id_wmo': '96791', 'lintang': -673440, 'bujur': 10826300, 'elevasi': 85},
    'Bandung-Kota': {'nama_stasiun': 'Stasiun Geofisika Bandung', 'id_wmo': '96783', 'lintang': -688356, 'bujur': 10759733, 'elevasi': 791},
    'Bogor-Kota': {'nama_stasiun': 'Stasiun Klimatologi Jawa Barat', 'id_wmo': '96753', 'lintang': -650000, 'bujur': 10675000, 'elevasi': 207}
}

conn = mysql.connector.connect(**db_config, connection_timeout=120)
cursor = conn.cursor()

logging.info("Connected to database successfully")

# ===== UTILITY =====
def convert_value(val):
    if pd.isna(val) or val == '-' or val == '' or str(val).strip() == '-':
        return None
    try:
        # Handle decimal comma (Indonesian format)
        if isinstance(val, str):
            val = val.replace(',', '.')
        return float(val)
    except:
        return None

def convert_wind_direction(val):
    # Fungsi khusus untuk arah angin (bisa huruf atau angka)
    if pd.isna(val) or val == '-' or val == '' or str(val).strip() == '-':
        return None
    return str(val).strip()

# ===== UPD INFO STASIUN =====
for loc_key, info in stasiun_info.items():
    nama_lokasi, jenis_lokasi = loc_key.split('-')
    
    cursor.execute("""
        UPDATE DimLokasi 
        SET nama_stasiun = %s, id_wmo = %s, lintang = %s, bujur = %s, elevasi = %s
        WHERE nama_lokasi = %s AND jenis_lokasi = %s
    """, (
        info['nama_stasiun'], 
        info['id_wmo'], 
        info['lintang'], 
        info['bujur'], 
        info['elevasi'],
        nama_lokasi,
        jenis_lokasi
    ))

conn.commit()
logging.info("Updated station information in DimLokasi")

# ===== PEMROSESAN DATA CSV =====
data_folder = 'Data'

# Iterasi setiap file CSV
for filename in os.listdir(data_folder):
    if filename.endswith('.csv') and 'BMKG' in filename:
        file_path = os.path.join(data_folder, filename)
        logging.info(f"Processing file: {file_path}")
        
        lokasi_name = filename.split('-')[-1].strip().replace('.csv', '')        
        jenis = 'Kabupaten' if 'Kab' in lokasi_name else 'Kota'
        lokasi_clean = lokasi_name.replace('Kab. ', '').replace('Kota ', '')
        logging.info(f"Location: {lokasi_clean}, Type: {jenis}")
        
        cursor.execute("SELECT lokasi_id FROM DimLokasi WHERE nama_lokasi = %s AND jenis_lokasi = %s", 
                      (lokasi_clean, jenis))
        result = cursor.fetchone()
        if not result:
            logging.error(f"Location not found: {lokasi_clean}, {jenis}")
            continue
            
        lokasi_id = result[0]
        
        try:
            df = pd.read_csv(file_path)
            logging.info(f"Read {len(df)} rows from {filename}")
        except Exception as e:
            logging.error(f"Error reading CSV file {filename}: {str(e)}")
            continue
        
        logging.info(f"Columns found: {', '.join(df.columns)}")
            
        # ===== PEMROSESAN BARIS DATA =====
        row_count = 0
        total_rows = len(df)
        log_interval = max(1, min(50, total_rows // 10))  # Progress logging
        
        logging.info(f"Starting to process {total_rows} rows of data")
        
        for _, row in df.iterrows():
            row_count += 1
            if row_count % log_interval == 0 or row_count == total_rows:
                logging.info(f"Progress: {row_count}/{total_rows} rows ({int(row_count/total_rows*100)}%) for {filename}")
            tanggal_col = 'TANGGAL' if 'TANGGAL' in df.columns else 'Tanggal'
            tanggal_str = row[tanggal_col]
            
            try:
                tanggal_obj = datetime.strptime(tanggal_str, '%d-%m-%Y').date()
            except:
                try:
                    tanggal_obj = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
                except:
                    logging.warning(f"Invalid date format: {tanggal_str}, skipping row")
                    continue
            
            cursor.execute("""
                INSERT IGNORE INTO DimWaktu (tanggal, bulan, tahun, nama_bulan)
                VALUES (%s, %s, %s, %s)
            """, (tanggal_obj, tanggal_obj.month, tanggal_obj.year, 
                  tanggal_obj.strftime('%B')))
            
            cursor.execute("SELECT waktu_id FROM DimWaktu WHERE tanggal = %s", (tanggal_obj,))
            waktu_id = cursor.fetchone()[0]
            
            # ===== MAPPING DAN KONVERSI DATA =====
            column_mapping = {
                'curah_hujan': 'RR',
                'suhu_min': 'TN',
                'suhu_max': 'TX',
                'suhu_rata': 'TAVG',
                'kelembaban_rata': 'RH_AVG',
                'lama_penyinaran': 'SS',
                'kecepatan_angin_max': 'FF_X',
                'arah_angin_max': 'DDD_X',
                'kecepatan_angin_rata': 'FF_AVG',
                'arah_angin_terbanyak': 'DDD_CAR'
            }
            
            data_values = {}
            for db_col, csv_col in column_mapping.items():
                if csv_col in df.columns:
                    val = row[csv_col]
                    if csv_col == 'RR' and (row_count % log_interval == 0):
                        logging.debug(f"Raw {csv_col} value: '{val}', type: {type(val)}")
                    
                    # Gunakan fungsi khusus untuk arah angin
                    if db_col in ['arah_angin_max', 'arah_angin_terbanyak']:
                        data_values[db_col] = convert_wind_direction(val)
                    else:
                        data_values[db_col] = convert_value(val)
                else:
                    data_values[db_col] = None
            
            # ===== END & SAVE KE DATABASE =====
            columns = ', '.join(['waktu_id', 'lokasi_id'] + list(data_values.keys()))
            placeholders = ', '.join(['%s'] * (2 + len(data_values)))
            values = [waktu_id, lokasi_id] + list(data_values.values())
            
            sql = f"INSERT INTO FactDataIklim (waktu_id, lokasi_id, {', '.join(data_values.keys())}) VALUES (%s, %s, {', '.join(['%s'] * len(data_values))})"
            
            try:
                cursor.execute(sql, values)
            except mysql.connector.Error as err:
                logging.error(f"Error inserting data: {err}")
                continue
        
        conn.commit()
        logging.info(f"Completed processing {filename}. Successfully imported {row_count} rows of data.")

cursor.close()
conn.close()
logging.info("Data import completed!")
