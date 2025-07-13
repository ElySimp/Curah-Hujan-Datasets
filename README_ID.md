# 🌦️ Dashboard Data Cuaca BMKG Jawa Barat

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com/)

> **Dashboard interaktif untuk data meteorologi Jawa Barat dari BMKG (Badan Meteorologi, Klimatologi, dan Geofisika)**

---

## 🌍 Versi Bahasa

- **🇺🇸 English**: [README.md](README.md)
- **🇮🇩 Indonesian**: README ini (saat ini)

---

## 📊 Gambaran Dashboard

Dashboard interaktif yang menyediakan analisis komprehensif data cuaca harian dari 5 kota/kabupaten di Jawa Barat, Indonesia. Dashboard ini memungkinkan pengguna untuk mengeksplorasi pola cuaca, membandingkan kondisi antar wilayah, dan menganalisis tren temporal dengan visualisasi yang informatif.

### 🎯 Fitur Utama

#### 🔧 **Sistem Multi-Filter**
- **Pilih Semua**: Menampilkan data dari semua 5 wilayah sekaligus
- **Pilih Beberapa Lokasi**: Membandingkan 2-4 wilayah tertentu
- **Pilih Satu Lokasi**: Fokus analisis pada satu wilayah
- **Filter Tanggal**: Rentang waktu yang dapat disesuaikan

#### 📈 **5 Tab Analisis Utama**

##### 1. 📊 **Ringkasan**
- Metrik utama: Total data, jumlah wilayah, rentang waktu, rata-rata curah hujan
- Analisis kelengkapan data per variabel cuaca
- Distribusi data per wilayah

##### 2. 🌧️ **Analisis Hujan**
- **Kategorisasi Intensitas**: Tidak hujan, ringan, sedang, lebat, sangat lebat
- **Pola Musiman**: Distribusi curah hujan sepanjang tahun
- **Perbandingan Wilayah**: Rata-rata, total, dan frekuensi hujan per lokasi
- **Heatmap Bulanan**: Pola hujan per bulan dan wilayah

##### 3. 🌡️ **Analisis Suhu**
- **Profil Suhu**: Minimum, rata-rata, maksimum per wilayah
- **Distribusi Temporal**: Variasi suhu sepanjang periode
- **Tren Bulanan**: Perubahan suhu musiman yang dapat dipilih jenisnya

##### 4. 💨 **Angin & Kelembaban**
- **Distribusi Kelembaban**: Box plot per wilayah
- **Pola Angin**: Histogram kecepatan angin
- **Statistik Perbandingan**: Min/max/rata-rata per wilayah
- **Korelasi Suhu-Kelembaban**: Scatter plot hubungan kedua variabel

##### 5. 📈 **Time Series**
- **Time Series Harian**: Perubahan variabel cuaca dari hari ke hari
- **Moving Average**: Tren halus dengan periode yang dapat disesuaikan (3-30 hari)
- **Multi-Variable**: Pilihan variabel cuaca (hujan, suhu, kelembaban, angin)

## 🗺️ Lokasi yang Dianalisis

| Wilayah | Jenis | Stasiun Meteorologi | ID WMO |
|---------|-------|-------------------|---------|
| **Bogor** | Kabupaten | Stasiun Meteorologi Citeko | 96751 |
| **Cirebon** | Kabupaten | Stasiun Klimatologi Jayapura | 97692 |
| **Majalengka** | Kabupaten | Stasiun Meteorologi Kertajati | 96791 |
| **Bandung** | Kota | Stasiun Geofisika Bandung | 96783 |
| **Bogor** | Kota | Stasiun Klimatologi Jawa Barat | 96753 |

## 📊 Variabel Cuaca yang Dianalisis

### 🌧️ **Curah Hujan (RR)**
- **Satuan**: Milimeter (mm)
- **Kategori**:
  - 0 mm: Tidak hujan
  - 1-5 mm: Hujan ringan
  - 6-20 mm: Hujan sedang
  - 21-50 mm: Hujan lebat
  - 50+ mm: Hujan sangat lebat

### 🌡️ **Suhu**
- **Suhu Minimum (TN)**: Suhu terdingin dalam sehari
- **Suhu Maksimum (TX)**: Suhu terpanas dalam sehari  
- **Suhu Rata-rata (TAVG)**: Rata-rata suhu sepanjang hari
- **Satuan**: Derajat Celsius (°C)

### 💨 **Angin**
- **Kecepatan Angin Rata-rata (FF_AVG)**: Rata-rata kecepatan angin harian
- **Kecepatan Angin Maksimum (FF_X)**: Kecepatan angin tertinggi dalam sehari
- **Arah Angin (DDD_X, DDD_CAR)**: Arah angin dominan
- **Satuan**: Meter per detik (m/s)

### 🌫️ **Kelembaban & Lainnya**
- **Kelembaban Rata-rata (RH_AVG)**: Persentase kelembaban udara (%)
- **Lama Penyinaran Matahari (SS)**: Durasi sinar matahari (jam)

## 🔧 Data Processing & Quality

### 📝 **Data Cleaning**
- **Kode Khusus Curah Hujan**:
  - `8888`: Tidak dapat diukur
  - `9999`: Tidak ada data
  - `-`: Data kosong
- **Penanganan**: Semua nilai khusus dikonversi menjadi NULL untuk analisis yang akurat

### 🏗️ **Database Schema (Star Schema)**
```sql
-- Tabel Dimensi Waktu
DimWaktu: waktu_id, tanggal, bulan, tahun, nama_bulan

-- Tabel Dimensi Lokasi  
DimLokasi: lokasi_id, nama_lokasi, jenis_lokasi, nama_stasiun, koordinat

-- Tabel Fakta Data Iklim
FactDataIklim: fact_id, waktu_id, lokasi_id, curah_hujan, suhu_min, 
               suhu_max, suhu_rata, kelembaban_rata, kecepatan_angin, etc.
```

## 🚀 Technology Stack

### **Backend**
- **Python 3.8+**: Bahasa pemrograman utama
- **MySQL**: Database untuk penyimpanan data terstruktur
- **pandas**: Manipulasi dan analisis data
- **mysql-connector-python**: Konektivitas database

### **Frontend & Visualisasi**
- **Streamlit**: Framework aplikasi web
- **Plotly**: Library visualisasi interaktif
- **Plotly Express**: Interface plotting tingkat tinggi

### **Deployment**
- **Streamlit Cloud**: Platform hosting untuk deployment
- **GitHub**: Version control dan repository management

## 📦 Instalasi & Setup

### **1. Clone Repository**
```bash
git clone https://github.com/ElySimp/Curah-Hujan-Datasets.git
cd Curah-Hujan-Datasets
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Environment Variables**
Buat file `.env`:
```env
MYSQL_HOST=your_host
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database
MYSQL_PORT=3306
```

### **4. Database Setup**
```bash
# Jalankan script SQL
mysql -u username -p < Scripts/CreateDB.sql
python Scripts/DBInput.py
```

### **5. Jalankan Dashboard**
```bash
streamlit run streamlit_dashboard.py
```

## 📁 Struktur Project

```
Curah-Hujan-Datasets/
├── 📊 streamlit_dashboard.py    # Aplikasi dashboard utama
├── 📋 requirements.txt          # Dependencies Python
├── 📖 README.md                 # Dokumentasi project (English)
├── 📖 README_ID.md             # Dokumentasi project (Indonesian)
├── 📁 Data/                     # File CSV mentah dari BMKG
│   ├── Data BMKG - Kab. Bogor.csv
│   ├── Data BMKG - Kab. Cirebon.csv
│   ├── Data BMKG - Kab. Majalengka.csv
│   ├── Data BMKG - Kota Bandung.csv
│   └── Data BMKG - Kota Bogor.csv
└── 📁 Scripts/                  # Script database dan processing
    ├── CreateDB.sql            # Pembuatan schema database
    ├── FixDB.sql              # Perbaikan database untuk arah angin
    ├── DBInput.py             # Script import data
    └── DBView.py              # Utilities untuk melihat database
```

## 🎯 Use Cases

### 🏛️ **Pemerintah & Perencanaan**
- Perencanaan infrastruktur berbasis pola cuaca
- Analisis risiko bencana meteorologi
- Kebijakan mitigasi perubahan iklim

### 🌾 **Pertanian & Agribisnis**
- Perencanaan jadwal tanam berdasarkan pola hujan
- Prediksi kebutuhan irigasi
- Optimalisasi hasil panen

### 🏢 **Penelitian & Akademis**
- Studi klimatologi regional Jawa Barat
- Analisis tren perubahan iklim
- Penelitian meteorologi terapan

### 🏗️ **Industri & Konstruksi**
- Perencanaan project berbasis cuaca
- Risk assessment untuk outdoor activities
- Optimalisasi operasional

## 📈 Dashboard Insights

### 🔍 **Kemampuan Analitis**
- **Temporal Analysis**: Identifikasi pola musiman dan tren jangka panjang
- **Spatial Comparison**: Perbandingan kondisi cuaca antar wilayah
- **Statistical Overview**: Statistik deskriptif komprehensif
- **Data Quality Assessment**: Evaluasi kelengkapan dan kualitas data

### 📊 **Jenis Visualisasi**
- **Time Series**: Line chart untuk tren temporal
- **Distribution**: Box plot, histogram, violin plot
- **Comparison**: Bar chart, heatmap
- **Correlation**: Scatter plot untuk hubungan antar variabel
- **Categorical**: Pie chart untuk distribusi kategorikal

## 🛠️ Technical Features

### ⚡ **Performance**
- **Caching**: Cache loading dan processing data untuk kecepatan
- **Lazy Loading**: Management memori yang efisien
- **Responsive**: Optimized untuk berbagai ukuran layar

### 🎨 **User Experience**
- **Clean Interface**: Design minimalis tanpa clutter
- **Interactive Filter**: Real-time filtering dengan feedback
- **Mobile Friendly**: Design responsive

### 🔒 **Data Security**
- **Environment Variables**: Kredensial database yang aman
- **Input Validation**: Input pengguna yang disanitasi
- **Error Handling**: Management error yang graceful

## 📚 Future Enhancements

### 🚀 **Fitur yang Direncanakan**
- [ ] **Forecasting**: Machine learning untuk prediksi cuaca
- [ ] **Export**: Download data dan visualisasi
- [ ] **Real-time Update**: Integrasi data live
- [ ] **Alert System**: Notifikasi untuk kondisi cuaca ekstrem
- [ ] **API Integration**: RESTful API untuk akses eksternal
- [ ] **Advanced Analytics**: Statistical testing dan modeling

### 🌐 **Skalabilitas**
- [ ] **Multi-Region**: Ekspansi ke provinsi lain
- [ ] **Historical Data**: Integrasi data historis lebih panjang
- [ ] **Satellite Data**: Integrasi data satelit cuaca
- [ ] **IoT Integration**: Real-time sensor data

## 👥 Contributing

Kami menyambut kontribusi! Silakan lihat panduan kontribusi kami:

1. **Fork** repository ini
2. **Buat** feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** perubahan Anda (`git commit -m 'Add some AmazingFeature'`)
4. **Push** ke branch (`git push origin feature/AmazingFeature`)
5. **Buka** Pull Request

## 📄 License

Project ini dilisensikan under MIT License - lihat file [LICENSE](LICENSE) untuk detail.

## 🙏 Acknowledgments

- **BMKG (Badan Meteorologi, Klimatologi, dan Geofisika)** untuk menyediakan data meteorologi
- **Tim Streamlit** untuk framework aplikasi web yang amazing
- **Tim Plotly** untuk tools visualisasi yang powerful
- **Open source community** untuk berbagai library dan tools

## 📞 Contact

**ElySimp**
- GitHub: [@ElySimp](https://github.com/ElySimp)
- Repository: [Curah-Hujan-Datasets](https://github.com/ElySimp/Curah-Hujan-Datasets)

---

<div align="center">

**🌦️ Dibuat dengan ❤️ untuk analisis data meteorologi Indonesia**

[![Star this repo](https://img.shields.io/github/stars/ElySimp/Curah-Hujan-Datasets?style=social)](https://github.com/ElySimp/Curah-Hujan-Datasets)
[![Fork this repo](https://img.shields.io/github/forks/ElySimp/Curah-Hujan-Datasets?style=social)](https://github.com/ElySimp/Curah-Hujan-Datasets/fork)

</div>
