# 🌦️ West Java Weather Data Dashboard

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com/)

> **Interactive weather dashboard for West Java meteorological data from BMKG (Indonesian Meteorological Agency)**

---

## 🌍 Language Versions

- **🇺🇸 English**: This README (current)
- **🇮🇩 Indonesian**: [README_ID.md](README_ID.md)

---

## 📊 Dashboard Overview

An interactive dashboard that provides comprehensive analysis of daily weather data from 5 cities/regencies in West Java, Indonesia. This dashboard enables users to explore weather patterns, compare conditions across regions, and analyze temporal trends with informative visualizations.

### 🎯 Key Features

#### 🔧 **Multi-Filter System**
- **Select All**: Display data from all 5 regions simultaneously
- **Select Multiple Locations**: Compare 2-4 specific regions
- **Select Single Location**: Focus analysis on one region
- **Date Filter**: Customizable time range selection

#### 📈 **5 Main Analysis Tabs**

##### 1. 📊 **Overview**
- Key metrics: Total data, number of regions, time range, average rainfall
- Data completeness analysis per weather variable
- Data distribution per region

##### 2. 🌧️ **Rainfall Analysis**
- **Intensity Categorization**: No rain, light, moderate, heavy, very heavy
- **Seasonal Patterns**: Rainfall distribution throughout the year
- **Regional Comparison**: Average, total, and frequency of rainfall per location
- **Monthly Heatmap**: Rainfall patterns per month and region

##### 3. 🌡️ **Temperature Analysis**
- **Temperature Profile**: Minimum, average, maximum per region
- **Temporal Distribution**: Temperature variation throughout the period
- **Monthly Trends**: Seasonal temperature changes with selectable types

##### 4. 💨 **Wind & Humidity**
- **Humidity Distribution**: Box plots per region
- **Wind Patterns**: Wind speed histograms
- **Comparative Statistics**: Min/max/average per region
- **Temperature-Humidity Correlation**: Scatter plot of variable relationships

##### 5. 📈 **Time Series**
- **Daily Time Series**: Day-to-day weather variable changes
- **Moving Average**: Smooth trends with adjustable periods (3-30 days)
- **Multi-Variable**: Weather variable selection (rain, temperature, humidity, wind)

## 🗺️ Analyzed Locations

| Region | Type | Meteorological Station | WMO ID |
|---------|-------|-------------------|---------|
| **Bogor** | Regency | Citeko Meteorological Station | 96751 |
| **Cirebon** | Regency | Jayapura Climatology Station | 97692 |
| **Majalengka** | Regency | Kertajati Meteorological Station | 96791 |
| **Bandung** | City | Bandung Geophysical Station | 96783 |
| **Bogor** | City | West Java Climatology Station | 96753 |

## 📊 Weather Variables Analyzed

### 🌧️ **Rainfall (RR)**
- **Unit**: Millimeter (mm)
- **Categories**:
  - 0 mm: No rain
  - 1-5 mm: Light rain
  - 6-20 mm: Moderate rain
  - 21-50 mm: Heavy rain
  - 50+ mm: Very heavy rain

### 🌡️ **Temperature**
- **Minimum Temperature (TN)**: Coldest temperature of the day
- **Maximum Temperature (TX)**: Hottest temperature of the day  
- **Average Temperature (TAVG)**: Daily average temperature
- **Unit**: Degrees Celsius (°C)

### 💨 **Wind**
- **Average Wind Speed (FF_AVG)**: Daily average wind speed
- **Maximum Wind Speed (FF_X)**: Highest wind speed of the day
- **Wind Direction (DDD_X, DDD_CAR)**: Dominant wind direction
- **Unit**: Meters per second (m/s)

### 🌫️ **Humidity & Others**
- **Average Humidity (RH_AVG)**: Air humidity percentage (%)
- **Sunshine Duration (SS)**: Duration of sunshine (hours)

## 🔧 Data Processing & Quality

### 📝 **Data Cleaning**
- **Special Rainfall Codes**:
  - `8888`: Cannot be measured
  - `9999`: No data available
  - `-`: Empty data
- **Handling**: All special values converted to NULL for accurate analysis

### 🏗️ **Database Schema (Star Schema)**
```sql
-- Time Dimension Table
DimWaktu: waktu_id, tanggal, bulan, tahun, nama_bulan

-- Location Dimension Table  
DimLokasi: lokasi_id, nama_lokasi, jenis_lokasi, nama_stasiun, koordinat

-- Climate Data Fact Table
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
- **Streamlit Cloud**: Hosting platform for deployment
- **GitHub**: Version control and repository management

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

### 🏛️ **Government & Planning**
- Infrastructure planning based on weather patterns
- Meteorological disaster risk analysis
- Climate change mitigation policies

### 🌾 **Agriculture & Agribusiness**
- Crop planting schedule based on rainfall patterns
- Irrigation needs prediction
- Harvest yield optimization

### 🏢 **Research & Academic**
- West Java regional climatology studies
- Climate change trend analysis
- Applied meteorology research

### 🏗️ **Industry & Construction**
- Weather-based project planning
- Risk assessment for outdoor activities
- Operational optimization

## 📈 Dashboard Insights

### 🔍 **Analytical Capabilities**
- **Temporal Analysis**: Identify seasonal patterns and long-term trends
- **Spatial Comparison**: Compare weather conditions across regions
- **Statistical Overview**: Comprehensive descriptive statistics
- **Data Quality Assessment**: Evaluate data completeness and quality

### 📊 **Visualization Types**
- **Time Series**: Line charts for temporal trends
- **Distribution**: Box plots, histograms, violin plots
- **Comparison**: Bar charts, heatmaps
- **Correlation**: Scatter plots for variable relationships
- **Categorical**: Pie charts for categorical distributions

## 🛠️ Technical Features

### ⚡ **Performance**
- **Caching**: Data loading and processing cache for speed
- **Lazy Loading**: Efficient memory management
- **Responsive**: Optimized for various screen sizes

### 🎨 **User Experience**
- **Clean Interface**: Minimalist design without clutter
- **Interactive Filters**: Real-time filtering with feedback
- **Mobile Friendly**: Responsive design

### 🔒 **Data Security**
- **Environment Variables**: Secure database credentials
- **Input Validation**: Sanitized user inputs
- **Error Handling**: Graceful error management

## 📚 Future Enhancements

### 🚀 **Planned Features**
- [ ] **Forecasting**: Machine learning for weather prediction
- [ ] **Export**: Download data and visualizations
- [ ] **Real-time Updates**: Live data integration
- [ ] **Alert System**: Notifications for extreme weather conditions
- [ ] **API Integration**: RESTful API for external access
- [ ] **Advanced Analytics**: Statistical testing and modeling

### 🌐 **Scalability**
- [ ] **Multi-Region**: Expansion to other provinces
- [ ] **Historical Data**: Integration of longer historical data
- [ ] **Satellite Data**: Weather satellite data integration
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