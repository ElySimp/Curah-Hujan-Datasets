import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Dashboard Data Cuaca BMKG",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk styling sederhana
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Database connection with SQLAlchemy
@st.cache_resource
def get_engine():
    """Membuat engine SQLAlchemy dengan connection pooling"""
    try:
        host = os.getenv('MYSQL_HOST')
        user = os.getenv('MYSQL_USER')
        password = os.getenv('MYSQL_PASSWORD')
        database = os.getenv('MYSQL_DATABASE')
        port = os.getenv('MYSQL_PORT', '3306')
        
        # Debugging info (hanya tampilkan jika ada masalah)
        if not all([host, user, password, database]):
            st.error("❌ Environment variables tidak lengkap!")
            st.write(f"Host: {host}, User: {user}, Database: {database}, Port: {port}")
            return None
        
        # Format URL koneksi untuk SQLAlchemy
        # mysql+mysqlconnector://<user>:<password>@<host>:<port>/<database>
        connection_url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
        
        engine = create_engine(
            connection_url,
            pool_recycle=3600,      # Reconnect setiap 1 jam
            pool_pre_ping=True,     # Test koneksi sebelum digunakan
            pool_size=5,            # Jumlah koneksi dalam pool
            max_overflow=10,        # Maksimal koneksi tambahan
            connect_args={
                'connect_timeout': 10,
                'autocommit': True
            }
        )
        
        # Test koneksi
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            # Pastikan query berhasil
            result.fetchone()
        
        return engine
        
    except Exception as e:
        st.error(f"❌ Gagal membuat engine database: {e}")
        return None

# Data loading functions
@st.cache_data(ttl=600)
def load_weather_data():
    """Memuat data cuaca dari database menggunakan SQLAlchemy"""
    engine = get_engine()
    if engine is None:
        return None
    
    query = """
    SELECT 
        f.*,
        w.tanggal,
        w.bulan,
        w.tahun,
        w.nama_bulan,
        l.nama_lokasi,
        l.jenis_lokasi,
        l.nama_stasiun
    FROM FactDataIklim f
    JOIN DimWaktu w ON f.waktu_id = w.waktu_id
    JOIN DimLokasi l ON f.lokasi_id = l.lokasi_id
    ORDER BY w.tanggal, l.nama_lokasi
    """
    
    try:
        # Menggunakan SQLAlchemy untuk query
        df = pd.read_sql(query, engine)
        
        if df.empty:
            return None
            
        # Pembersihan data
        df = clean_weather_data(df)
        
        return df
        
    except Exception as e:
        # Return None dengan error info dalam tuple
        return None

def clean_weather_data(df):
    """Membersihkan data cuaca dengan menangani nilai khusus"""
    # Menangani kode khusus untuk curah hujan
    df['curah_hujan_clean'] = df['curah_hujan'].apply(lambda x: 
        None if x in [8888, 9999] or pd.isna(x) else x)
    
    # Membuat kategori curah hujan
    df['curah_hujan_kategori'] = df['curah_hujan_clean'].apply(categorize_rainfall)
    
    # Membuat nama lokasi lengkap
    df['lokasi_lengkap'] = df['nama_lokasi'] + ' (' + df['jenis_lokasi'] + ')'
    
    # Konversi kolom tanggal
    df['tanggal'] = pd.to_datetime(df['tanggal'])
    
    return df

def categorize_rainfall(value):
    """Mengkategorikan intensitas curah hujan"""
    if pd.isna(value) or value is None:
        return 'Tidak Ada Data'
    elif value == 0:
        return 'Tidak Hujan'
    elif value <= 5:
        return 'Hujan Ringan'
    elif value <= 20:
        return 'Hujan Sedang'
    elif value <= 50:
        return 'Hujan Lebat'
    else:
        return 'Hujan Sangat Lebat'

def get_consistent_colors():
    """Mengembalikan mapping warna konsisten untuk kategori dan lokasi"""
    rainfall_colors = {
        'Tidak Ada Data': '#d3d3d3',      # Abu-abu
        'Tidak Hujan': '#87ceeb',         # Biru muda  
        'Hujan Ringan': '#90ee90',        # Hijau muda
        'Hujan Sedang': '#ffd700',        # Kuning
        'Hujan Lebat': '#ffa500',         # Orange
        'Hujan Sangat Lebat': '#ff4500'   # Merah orange
    }
    
    location_colors = {
        'Bogor (Kabupaten)': '#1f77b4',
        'Bogor (Kota)': '#ff7f0e', 
        'Bandung (Kota)': '#2ca02c',
        'Cirebon (Kabupaten)': '#d62728',
        'Majalengka (Kabupaten)': '#9467bd'
    }
    
    return rainfall_colors, location_colors

# Main dashboard
def main():
    st.markdown('<h1 class="main-header">🌦️ Dashboard Data Cuaca BMKG Jawa Barat</h1>', unsafe_allow_html=True)
    
    # Memuat data
    with st.spinner('Memuat data cuaca...'):
        df = load_weather_data()
    
    if df is None or df.empty:
        st.error("Data tidak tersedia. Silakan periksa koneksi database dan data.")
        return
    
    # Toast notification setelah data berhasil dimuat
    st.toast(f"✅ Data dimuat: {len(df):,} records dari {df['lokasi_lengkap'].nunique()} lokasi", icon="📊")

    # Filter di sidebar
    st.sidebar.header("🔧 Pengaturan Filter")
    
    # Tombol untuk clear cache jika ada masalah
    if st.sidebar.button("🔄 Refresh Data", help="Klik jika data tidak muncul"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()
    
    # Filter lokasi dengan opsi multi-select
    all_locations = sorted(df['lokasi_lengkap'].unique().tolist())
    
    # Pilihan mode filter
    filter_mode = st.sidebar.radio(
        "Mode Pemilihan Lokasi:",
        ["Pilih Semua", "Pilih Beberapa Lokasi", "Pilih Satu Lokasi"]
    )
    
    if filter_mode == "Pilih Semua":
        selected_locations = all_locations
        st.sidebar.success(f"Menampilkan semua {len(all_locations)} lokasi")
    elif filter_mode == "Pilih Beberapa Lokasi":
        selected_locations = st.sidebar.multiselect(
            "Pilih 2-4 lokasi untuk dibandingkan:",
            all_locations,
            default=all_locations[:3],  # Default 3 lokasi pertama
            help="Pilih maksimal 4 lokasi untuk perbandingan yang optimal"
        )
        if len(selected_locations) > 4:
            st.sidebar.warning("⚠️ Maksimal 4 lokasi untuk visualisasi yang jelas")
            selected_locations = selected_locations[:4]
    else:  # Pilih satu lokasi
        selected_location = st.sidebar.selectbox("Pilih satu lokasi:", all_locations)
        selected_locations = [selected_location]
    
    # Filter tanggal
    min_date = df['tanggal'].min()
    max_date = df['tanggal'].max()
    date_range = st.sidebar.date_input(
        "Pilih Periode Waktu:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Pilih rentang tanggal untuk analisis"
    )
    
    # Filter data berdasarkan pilihan
    filtered_df = df[df['lokasi_lengkap'].isin(selected_locations)].copy()
    
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['tanggal'] >= pd.to_datetime(date_range[0])) &
            (filtered_df['tanggal'] <= pd.to_datetime(date_range[1]))
        ]
    
    # Tampilkan informasi filter yang aktif
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📊 Filter Aktif:**")
    st.sidebar.write(f"• Lokasi: {len(selected_locations)} wilayah")
    st.sidebar.write(f"• Data: {len(filtered_df):,} hari")
    
    # Credit di sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("**👨‍💻 Dibuat oleh:**")
    st.sidebar.markdown("**ElySimp's Team**")
    st.sidebar.markdown("- Faldo Maxwell")
    st.sidebar.markdown("- Michael Jeconiah Yonathan")
    st.sidebar.markdown("- Rafael Austin")
    st.sidebar.markdown("- Andhika Dwi Rachmawanto")
    st.sidebar.markdown("- Alfi Syahrian")
    st.sidebar.markdown("[📁 GitHub Repository](https://github.com/ElySimp/Curah-Hujan-Datasets)")
    st.sidebar.markdown("---")
    
    # Tab utama dengan nama yang lebih sederhana
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Ringkasan", "🌧️ Analisis Hujan", "🌡️ Suhu", "💨 Angin & Kelembaban", "📈 Grafik Waktu"
    ])
    
    with tab1:
        overview_tab(filtered_df)
    
    with tab2:
        rainfall_tab(filtered_df)
    
    with tab3:
        temperature_tab(filtered_df)
    
    with tab4:
        wind_humidity_tab(filtered_df)
    
    with tab5:
        timeseries_tab(filtered_df)

def overview_tab(df):
    """Tab ringkasan data"""
    st.subheader("📊 Ringkasan Data Cuaca")
    
    # Metrik utama
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_records = len(df)
        st.metric("Total Data Harian", f"{total_records:,}")
    
    with col2:
        unique_locations = df['lokasi_lengkap'].nunique()
        st.metric("Jumlah Wilayah", unique_locations)
    
    with col3:
        date_range = (df['tanggal'].max() - df['tanggal'].min()).days
        st.metric("Rentang Waktu (hari)", date_range)
    
    with col4:
        avg_rainfall = df['curah_hujan_clean'].mean()
        st.metric("Rata-rata Hujan Harian", f"{avg_rainfall:.1f} mm" if not pd.isna(avg_rainfall) else "Tidak ada data")
    
    # Kualitas data
    st.subheader("📋 Kelengkapan Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Ringkasan data yang hilang
        missing_data = pd.DataFrame({
            'Jenis Data': ['Curah Hujan', 'Suhu Minimum', 'Suhu Maksimum', 'Kelembaban', 'Kecepatan Angin'],
            'Data Hilang (%)': [
                (df['curah_hujan_clean'].isna().sum() / len(df)) * 100,
                (df['suhu_min'].isna().sum() / len(df)) * 100,
                (df['suhu_max'].isna().sum() / len(df)) * 100,
                (df['kelembaban_rata'].isna().sum() / len(df)) * 100,
                (df['kecepatan_angin_rata'].isna().sum() / len(df)) * 100
            ]
        })
        
        fig_missing = px.bar(missing_data, x='Jenis Data', y='Data Hilang (%)', 
                           title="Persentase Data yang Hilang",
                           color='Data Hilang (%)',
                           color_continuous_scale='Reds')
        fig_missing.update_layout(height=400)
        st.plotly_chart(fig_missing, use_container_width=True)
    
    with col2:
        # Distribusi data per lokasi
        location_counts = df.groupby('lokasi_lengkap').size().reset_index(name='Jumlah_Data')
        fig_location = px.pie(location_counts, values='Jumlah_Data', names='lokasi_lengkap',
                            title="Distribusi Data per Wilayah")
        fig_location.update_layout(height=400)
        st.plotly_chart(fig_location, use_container_width=True)

def rainfall_tab(df):
    """Tab analisis curah hujan"""
    st.subheader("🌧️ Analisis Curah Hujan")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribusi kategori hujan dengan warna konsisten
        rainfall_dist = df['curah_hujan_kategori'].value_counts()
        
        # Gunakan warna konsisten
        rainfall_colors, _ = get_consistent_colors()
        
        # Buat list warna sesuai urutan kategori yang muncul
        colors = [rainfall_colors.get(category, '#cccccc') for category in rainfall_dist.index]
        
        fig_dist = px.pie(values=rainfall_dist.values, names=rainfall_dist.index,
                         title="Sebaran Intensitas Hujan",
                         color_discrete_sequence=colors)
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with col2:
        # Hujan bulanan dengan warna konsisten per lokasi
        monthly_rainfall = df.groupby(['nama_bulan', 'lokasi_lengkap'])['curah_hujan_clean'].mean().reset_index()
        
        # Warna konsisten untuk lokasi
        location_colors = {
            'Bogor (Kabupaten)': '#1f77b4',
            'Bogor (Kota)': '#ff7f0e', 
            'Bandung (Kota)': '#2ca02c',
            'Cirebon (Kabupaten)': '#d62728',
            'Majalengka (Kabupaten)': '#9467bd'
        }
        
        fig_monthly = px.box(monthly_rainfall, x='nama_bulan', y='curah_hujan_clean',
                           title="Pola Hujan Sepanjang Tahun",
                           labels={'curah_hujan_clean': 'Curah Hujan (mm)', 'nama_bulan': 'Bulan'})
        fig_monthly.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    # Perbandingan hujan antar lokasi
    st.subheader("📊 Perbandingan Hujan Antar Wilayah")
    
    location_rainfall = df.groupby('lokasi_lengkap').agg({
        'curah_hujan_clean': ['mean', 'sum', 'count']
    }).round(2)
    location_rainfall.columns = ['Rata-rata Harian (mm)', 'Total (mm)', 'Hari dengan Data']
    
    st.dataframe(location_rainfall, use_container_width=True)
    
    # Heatmap jika ada multiple lokasi
    if df['lokasi_lengkap'].nunique() > 1:
        st.subheader("🗓️ Pola Hujan Bulanan per Wilayah")
        
        pivot_rainfall = df.pivot_table(
            values='curah_hujan_clean', 
            index='lokasi_lengkap', 
            columns='nama_bulan', 
            aggfunc='mean'
        )
        
        fig_heatmap = px.imshow(pivot_rainfall, 
                              title="Rata-rata Curah Hujan Bulanan (mm)",
                              color_continuous_scale="Blues",
                              labels={'x': 'Bulan', 'y': 'Wilayah', 'color': 'Hujan (mm)'})
        st.plotly_chart(fig_heatmap, use_container_width=True)

def temperature_tab(df):
    """Tab analisis suhu"""
    st.subheader("🌡️ Analisis Suhu")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Rentang suhu per lokasi dengan warna konsisten
        temp_stats = df.groupby('lokasi_lengkap').agg({
            'suhu_min': 'mean',
            'suhu_max': 'mean',
            'suhu_rata': 'mean'
        }).round(1)
        
        # Gunakan warna konsisten untuk lokasi
        _, location_colors = get_consistent_colors()
        
        fig_temp = go.Figure()
        
        for i, location in enumerate(temp_stats.index):
            color = location_colors.get(location, px.colors.qualitative.Set2[i % len(px.colors.qualitative.Set2)])
            fig_temp.add_trace(go.Scatter(
                x=['Minimum', 'Rata-rata', 'Maksimum'],
                y=[temp_stats.loc[location, 'suhu_min'], 
                   temp_stats.loc[location, 'suhu_rata'],
                   temp_stats.loc[location, 'suhu_max']],
                mode='lines+markers',
                name=location,
                line=dict(width=3, color=color),
                marker=dict(size=8)
            ))
        
        fig_temp.update_layout(
            title="Profil Suhu Rata-rata per Wilayah",
            xaxis_title="Jenis Suhu",
            yaxis_title="Suhu (°C)",
            height=400
        )
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with col2:
        # Distribusi suhu
        temp_melted = pd.melt(df[['lokasi_lengkap', 'suhu_min', 'suhu_max', 'suhu_rata']], 
                            id_vars=['lokasi_lengkap'],
                            var_name='jenis_suhu', value_name='suhu')
        
        # Ganti nama kolom untuk lebih mudah dipahami
        temp_melted['jenis_suhu'] = temp_melted['jenis_suhu'].map({
            'suhu_min': 'Minimum',
            'suhu_max': 'Maksimum', 
            'suhu_rata': 'Rata-rata'
        })
        
        fig_violin = px.violin(temp_melted, x='jenis_suhu', y='suhu',
                             title="Distribusi Suhu",
                             box=True,
                             labels={'suhu': 'Suhu (°C)', 'jenis_suhu': 'Jenis Suhu'})
        st.plotly_chart(fig_violin, use_container_width=True)
    
    # Tren suhu bulanan
    st.subheader("📈 Tren Suhu Sepanjang Tahun")
    monthly_temp = df.groupby(['nama_bulan', 'lokasi_lengkap']).agg({
        'suhu_min': 'mean',
        'suhu_max': 'mean',
        'suhu_rata': 'mean'
    }).reset_index()
    
    # Gunakan warna konsisten
    _, location_colors = get_consistent_colors()
    
    # Pilihan jenis suhu untuk ditampilkan
    temp_type = st.selectbox(
        "Pilih jenis suhu:",
        ["suhu_rata", "suhu_min", "suhu_max"],
        format_func=lambda x: {"suhu_rata": "Suhu Rata-rata", "suhu_min": "Suhu Minimum", "suhu_max": "Suhu Maksimum"}[x]
    )
    
    fig_monthly_temp = px.line(monthly_temp, x='nama_bulan', y=temp_type,
                             color='lokasi_lengkap',
                             title=f"Tren {temp_type.replace('_', ' ').title()} Bulanan",
                             labels={temp_type: 'Suhu (°C)', 'nama_bulan': 'Bulan'},
                             markers=True,
                             color_discrete_map=location_colors)
    fig_monthly_temp.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_monthly_temp, use_container_width=True)

def wind_humidity_tab(df):
    """Tab analisis angin dan kelembaban"""
    st.subheader("💨 Analisis Angin & Kelembaban")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribusi kelembaban
        fig_humidity = px.box(df, x='lokasi_lengkap', y='kelembaban_rata',
                            title="Tingkat Kelembaban per Wilayah",
                            labels={'kelembaban_rata': 'Kelembaban (%)', 'lokasi_lengkap': 'Wilayah'})
        fig_humidity.update_xaxes(tickangle=45)
        st.plotly_chart(fig_humidity, use_container_width=True)
    
    with col2:
        # Distribusi kecepatan angin
        fig_wind = px.histogram(df, x='kecepatan_angin_rata', nbins=30,
                              title="Distribusi Kecepatan Angin",
                              labels={'kecepatan_angin_rata': 'Kecepatan Angin (m/s)', 'count': 'Jumlah Hari'})
        st.plotly_chart(fig_wind, use_container_width=True)
    
    # Perbandingan antar wilayah
    st.subheader("📊 Perbandingan Kondisi Udara Antar Wilayah")
    
    # Statistik per wilayah
    wind_humidity_stats = df.groupby('lokasi_lengkap').agg({
        'kelembaban_rata': ['mean', 'min', 'max'],
        'kecepatan_angin_rata': ['mean', 'min', 'max']
    }).round(2)
    
    wind_humidity_stats.columns = [
        'Kelembaban Rata-rata (%)', 'Kelembaban Min (%)', 'Kelembaban Max (%)',
        'Angin Rata-rata (m/s)', 'Angin Min (m/s)', 'Angin Max (m/s)'
    ]
    
    st.dataframe(wind_humidity_stats, use_container_width=True)
    
    # Hubungan kelembaban dan suhu
    if len(df) > 0:
        st.subheader("🌡️ Hubungan Kelembaban dan Suhu")
        
        # Gunakan warna konsisten
        _, location_colors = get_consistent_colors()
        
        fig_scatter = px.scatter(df, x='suhu_rata', y='kelembaban_rata', 
                               color='lokasi_lengkap',
                               title="Hubungan antara Suhu dan Kelembaban",
                               labels={'suhu_rata': 'Suhu Rata-rata (°C)', 
                                      'kelembaban_rata': 'Kelembaban (%)'},
                               color_discrete_map=location_colors)
        st.plotly_chart(fig_scatter, use_container_width=True)

def timeseries_tab(df):
    """Tab analisis grafik waktu"""
    st.subheader("📈 Analisis Grafik Sepanjang Waktu")
    
    # Pilihan variabel untuk time series
    variables = {
        'Curah Hujan (mm)': 'curah_hujan_clean',
        'Suhu Rata-rata (°C)': 'suhu_rata',
        'Kelembaban (%)': 'kelembaban_rata',
        'Kecepatan Angin (m/s)': 'kecepatan_angin_rata'
    }
    
    selected_var = st.selectbox("Pilih data cuaca:", list(variables.keys()))
    
    # Gunakan warna konsisten
    _, location_colors = get_consistent_colors()
    
    # Grafik time series
    if df['lokasi_lengkap'].nunique() > 1:
        daily_data = df.groupby(['tanggal', 'lokasi_lengkap'])[variables[selected_var]].mean().reset_index()
        
        fig_ts = px.line(daily_data, x='tanggal', y=variables[selected_var],
                        color='lokasi_lengkap',
                        title=f"Grafik Harian: {selected_var}",
                        labels={'tanggal': 'Tanggal', variables[selected_var]: selected_var},
                        color_discrete_map=location_colors)
        fig_ts.update_layout(height=500)
        st.plotly_chart(fig_ts, use_container_width=True)
    else:
        daily_data = df.groupby('tanggal')[variables[selected_var]].mean().reset_index()
        
        fig_ts = px.line(daily_data, x='tanggal', y=variables[selected_var],
                        title=f"Grafik Harian: {selected_var}",
                        labels={'tanggal': 'Tanggal', variables[selected_var]: selected_var})
        fig_ts.update_layout(height=500)
        st.plotly_chart(fig_ts, use_container_width=True)
    
    # Moving averages
    st.subheader("📊 Rata-rata Bergerak")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        window_size = st.slider("Periode rata-rata (hari):", 
                               min_value=3, max_value=30, value=7)
    
    # Hitung moving averages untuk setiap lokasi
    ma_data = []
    for location in df['lokasi_lengkap'].unique():
        location_data = df[df['lokasi_lengkap'] == location].copy()
        location_data = location_data.sort_values('tanggal')
        location_data[f'MA_{window_size}'] = location_data[variables[selected_var]].rolling(
            window=window_size, center=True).mean()
        ma_data.append(location_data)
    
    ma_df = pd.concat(ma_data)
    
    fig_ma = px.line(ma_df, x='tanggal', y=f'MA_{window_size}',
                    color='lokasi_lengkap',
                    title=f"Tren {selected_var} (Rata-rata {window_size} Hari)",
                    labels={'tanggal': 'Tanggal', f'MA_{window_size}': f'{selected_var} (Rata-rata)'},
                    color_discrete_map=location_colors)
    fig_ma.update_layout(height=500)
    st.plotly_chart(fig_ma, use_container_width=True)

if __name__ == "__main__":
    main()
