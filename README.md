# 🌦️ Dashboard Data Cuaca BMKG Jawa Barat

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com/)

> **Interactive weather dashboard for West Java meteorological data from BMKG (Indonesian Meteorological Agency)**

## 📊 Dashboard Overview

Dashboard interaktif yang menampilkan analisis komprehensif data cuaca harian dari 5 kota/kabupaten di Jawa Barat. Dashboard ini memungkinkan pengguna untuk mengeksplorasi pola cuaca, membandingkan kondisi antar wilayah, dan menganalisis tren temporal dengan visualisasi yang informatif.

### 🎯 Fitur Utama

#### 🔧 **Multi-Filter System**
- **Pilih Semua**: Menampilkan data dari semua 5 wilayah sekaligus
- **Pilih Beberapa Lokasi**: Membandingkan 2-4 wilayah tertentu
- **Pilih Satu Lokasi**: Fokus analisis pada satu wilayah
- **Filter Tanggal**: Rentang waktu yang dapat disesuaikan

#### 🌓 **Dark/Light Mode**
- Toggle tema gelap/terang untuk kenyamanan viewing
- Responsif dengan semua visualisasi

#### 📈 **5 Tab Analisis Utama**

##### 1. 📊 **Ringkasan**
- Metrik kunci: Total data, jumlah wilayah, rentang waktu, rata-rata curah hujan
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
- **Tren Bulanan**: Perubahan suhu seasonal yang dapat dipilih jenisnya

##### 4. 💨 **Angin & Kelembaban**
- **Distribusi Kelembaban**: Box plot per wilayah
- **Pola Angin**: Histogram kecepatan angin
- **Statistik Komparatif**: Min/max/rata-rata per wilayah
- **Korelasi Suhu-Kelembaban**: Scatter plot hubungan kedua variabel

##### 5. 📈 **Grafik Waktu**
- **Time Series Harian**: Grafik perubahan variabel cuaca dari hari ke hari
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
- **Handling**: Semua nilai khusus dikonversi menjadi NULL untuk analisis yang akurat

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
- **Python 3.8+**: Core programming language
- **MySQL**: Database untuk penyimpanan data terstruktur
- **pandas**: Data manipulation dan analysis
- **mysql-connector-python**: Database connectivity

### **Frontend & Visualization**
- **Streamlit**: Web application framework
- **Plotly**: Interactive visualization library
- **Plotly Express**: High-level plotting interface

### **Deployment**
- **Streamlit Cloud**: Platform hosting untuk deployment
- **GitHub**: Version control dan repository management

## 📦 Installation & Setup

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
Create `.env` file:
```env
MYSQL_HOST=your_host
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database
MYSQL_PORT=3306
```

### **4. Database Setup**
```bash
# Run SQL scripts
mysql -u username -p < Scripts/CreateDB.sql
python Scripts/DBInput.py
```

### **5. Run Dashboard**
```bash
streamlit run streamlit_dashboard.py
```

## 📁 Project Structure

```
Curah-Hujan-Datasets/
├── 📊 streamlit_dashboard.py    # Main dashboard application
├── 📋 requirements.txt          # Python dependencies
├── 📖 README.md                 # Project documentation
├── 📁 Data/                     # Raw CSV files from BMKG
│   ├── Data BMKG - Kab. Bogor.csv
│   ├── Data BMKG - Kab. Cirebon.csv
│   ├── Data BMKG - Kab. Majalengka.csv
│   ├── Data BMKG - Kota Bandung.csv
│   └── Data BMKG - Kota Bogor.csv
└── 📁 Scripts/                  # Database and processing scripts
    ├── CreateDB.sql            # Database schema creation
    ├── FixDB.sql              # Database fixes for wind direction
    ├── DBInput.py             # Data import script
    └── DBView.py              # Database viewing utilities
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
- Penelitian meteorologi applied

### 🏗️ **Industri & Konstruksi**
- Perencanaan proyek berbasis cuaca
- Risk assessment untuk outdoor activities
- Optimalisasi operasional

## 📈 Dashboard Insights

### 🔍 **Analytical Capabilities**
- **Temporal Analysis**: Identifikasi pola seasonal dan trend jangka panjang
- **Spatial Comparison**: Perbandingan kondisi cuaca antar wilayah
- **Statistical Overview**: Deskriptif statistik komprehensif
- **Data Quality Assessment**: Evaluasi kelengkapan dan kualitas data

### 📊 **Visualization Types**
- **Time Series**: Line charts untuk trend temporal
- **Distribution**: Box plots, histograms, violin plots
- **Comparison**: Bar charts, heatmaps
- **Correlation**: Scatter plots untuk hubungan antar variabel
- **Categorical**: Pie charts untuk distribusi kategorikal

## 🛠️ Technical Features

### ⚡ **Performance**
- **Caching**: Data loading dan processing cache untuk speed
- **Lazy Loading**: Efficient memory management
- **Responsive**: Optimized untuk berbagai screen sizes

### 🎨 **User Experience**
- **Clean Interface**: Minimalist design tanpa clutter
- **Interactive Filters**: Real-time filtering dengan feedback
- **Theme Support**: Dark/light mode toggle
- **Mobile Friendly**: Responsive design

### 🔒 **Data Security**
- **Environment Variables**: Secure database credentials
- **Input Validation**: Sanitized user inputs
- **Error Handling**: Graceful error management

## 📚 Future Enhancements

### 🚀 **Planned Features**
- [ ] **Forecasting**: Machine learning untuk prediksi cuaca
- [ ] **Export**: Download data dan visualizations
- [ ] **Real-time Updates**: Live data integration
- [ ] **Alert System**: Notifikasi untuk kondisi cuaca ekstrem
- [ ] **API Integration**: RESTful API untuk external access
- [ ] **Advanced Analytics**: Statistical testing dan modeling

### 🌐 **Scalability**
- [ ] **Multi-Region**: Ekspansi ke provinsi lain
- [ ] **Historical Data**: Integrasi data historis lebih panjang
- [ ] **Satellite Data**: Integrasi data satelit cuaca
- [ ] **IoT Integration**: Real-time sensor data

## 👥 Contributing

We welcome contributions! Please see our contributing guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **BMKG (Badan Meteorologi, Klimatologi, dan Geofisika)** for providing meteorological data
- **Streamlit** team for the amazing web app framework
- **Plotly** team for powerful visualization tools
- **Open source community** for various libraries and tools

## 📞 Contact

**ElySimp**
- GitHub: [@ElySimp](https://github.com/ElySimp)
- Repository: [Curah-Hujan-Datasets](https://github.com/ElySimp/Curah-Hujan-Datasets)

---

<div align="center">

**🌦️ Made with ❤️ for Indonesian meteorological data analysis**

[![Star this repo](https://img.shields.io/github/stars/ElySimp/Curah-Hujan-Datasets?style=social)](https://github.com/ElySimp/Curah-Hujan-Datasets)
[![Fork this repo](https://img.shields.io/github/forks/ElySimp/Curah-Hujan-Datasets?style=social)](https://github.com/ElySimp/Curah-Hujan-Datasets/fork)

</div>