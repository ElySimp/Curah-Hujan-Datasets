#!/usr/bin/env python3
"""
Script untuk test koneksi database MySQL
"""

import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test koneksi ke database MySQL"""
    print("🔍 Testing koneksi database...")
    print(f"Host: {os.getenv('MYSQL_HOST')}")
    print(f"User: {os.getenv('MYSQL_USER')}")
    print(f"Database: {os.getenv('MYSQL_DATABASE')}")
    print(f"Port: {os.getenv('MYSQL_PORT')}")
    print("-" * 50)
    
    try:
        # Test koneksi
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE'),
            port=int(os.getenv('MYSQL_PORT')),
            connection_timeout=10  # 10 detik timeout
        )
        
        print("✅ Koneksi berhasil!")
        
        # Test query sederhana
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM FactDataIklim")
        count = cursor.fetchone()[0]
        print(f"✅ Jumlah data di FactDataIklim: {count:,} records")
        
        cursor.execute("SELECT COUNT(*) FROM DimLokasi")
        count = cursor.fetchone()[0]
        print(f"✅ Jumlah lokasi di DimLokasi: {count} lokasi")
        
        cursor.execute("SELECT COUNT(*) FROM DimWaktu")
        count = cursor.fetchone()[0]
        print(f"✅ Jumlah waktu di DimWaktu: {count} hari")
        
        cursor.close()
        connection.close()
        
        print("\n🎉 Database siap digunakan!")
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Error koneksi MySQL: {e}")
        print(f"Error Code: {e.errno}")
        print(f"Error Message: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Error umum: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    if not success:
        print("\n💡 Solusi yang bisa dicoba:")
        print("1. Periksa koneksi internet")
        print("2. Pastikan server database online")
        print("3. Periksa kredensial di file .env")
        print("4. Pastikan IP/hostname benar")
        print("5. Periksa firewall/port 3306")
