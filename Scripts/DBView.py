import mysql.connector
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Koneksi database dari .env
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'port': int(os.getenv('MYSQL_PORT'))
}

def view_table(conn, table_name, limit=10):
    """Menampilkan isi tabel dalam format tabular"""
    print(f"\n=== {table_name} ===")
    query = f"SELECT * FROM {table_name} LIMIT {limit}"
    
    try:
        df = pd.read_sql(query, conn)
        if len(df) == 0:
            print(f"Tabel {table_name} kosong.")
        else:
            print(df)
            print(f"Total baris: {pd.read_sql(f'SELECT COUNT(*) as count FROM {table_name}', conn)['count'].iloc[0]}")
    except Exception as e:
        print(f"Error membaca tabel {table_name}: {str(e)}")

def check_database():
    try:
        conn = mysql.connector.connect(**db_config)
        
        # Cek tabel yang ada
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"Tabel yang ada di database: {', '.join(tables)}")
        
        # Lihat isi setiap tabel
        if 'DimLokasi' in tables:
            view_table(conn, 'DimLokasi')
        
        if 'DimWaktu' in tables:
            view_table(conn, 'DimWaktu')
        
        if 'FactDataIklim' in tables:
            view_table(conn, 'FactDataIklim')
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")

if __name__ == "__main__":
    check_database()