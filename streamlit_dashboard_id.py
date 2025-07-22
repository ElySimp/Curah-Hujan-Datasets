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
        
        if not all([host, user, password, database]):
            st.error("❌ Environment variables tidak lengkap!")
            st.write(f"Host: {host}, User: {user}, Database: {database}, Port: {port}")
            return None
        
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
    df['curah_hujan_clean'] = df['curah_hujan'].apply(lambda x: 
        None if x in [8888, 9999] or pd.isna(x) else x)
    
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
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Ringkasan", "🌧️ Analisis Hujan", "🌡️ Suhu", "💨 Angin & Kelembaban", "📈 Grafik Waktu", "📋 Pivot Table"
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
    
    with tab6:
        pivot_table_tab(filtered_df)

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
        # Distribusi kategori hujan dengan warna konsisten dan urutan yang tetap
        rainfall_dist = df['curah_hujan_kategori'].value_counts()
        
        # Urutan kategori yang diinginkan (hardcoded untuk konsistensi)
        category_order = [
            'Tidak Ada Data',
            'Tidak Hujan',
            'Hujan Ringan',
            'Hujan Sedang',
            'Hujan Lebat',
            'Hujan Sangat Lebat'
        ]
        
        # Gunakan warna konsisten
        rainfall_colors, _ = get_consistent_colors()
        
        # Reorder data sesuai urutan yang diinginkan
        ordered_categories = []
        ordered_values = []
        ordered_colors = []
        
        for category in category_order:
            if category in rainfall_dist.index:
                ordered_categories.append(category)
                ordered_values.append(rainfall_dist[category])
                ordered_colors.append(rainfall_colors.get(category, '#cccccc'))
        
        # Buat DataFrame untuk kontrol penuh atas urutan
        pie_data = pd.DataFrame({
            'kategori': ordered_categories,
            'nilai': ordered_values,
            'warna': ordered_colors
        })
        
        fig_dist = px.pie(pie_data, 
                         values='nilai', 
                         names='kategori',
                         title="Sebaran Intensitas Hujan",
                         color_discrete_sequence=ordered_colors,
                         category_orders={'kategori': category_order})
        
        # Pastikan urutan legend tetap konsisten
        fig_dist.update_traces(sort=False)
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
        
        # Definisi urutan bulan yang benar (dalam bahasa Inggris sesuai database)
        month_order = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        
        pivot_rainfall = df.pivot_table(
            values='curah_hujan_clean', 
            index='lokasi_lengkap', 
            columns='nama_bulan', 
            aggfunc='mean'
        )
        
        # Urutkan kolom berdasarkan urutan bulan yang benar
        available_months = [month for month in month_order if month in pivot_rainfall.columns]
        pivot_rainfall = pivot_rainfall.reindex(columns=available_months)
        
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

def pivot_table_tab(df):
    """Tab untuk analisis pivot table interaktif"""
    st.subheader("📋 Analisis Pivot Table")
    
    # Definisi urutan bulan yang benar (dalam bahasa Inggris sesuai database)
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    # Pilihan jenis pivot table
    pivot_type = st.selectbox(
        "Pilih jenis analisis pivot table:",
        [
            "Curah Hujan Bulanan per Lokasi",
            "Statistik Cuaca per Wilayah",
            "Analisis Musiman",
            "Pivot Table Kustom"
        ]
    )
    
    if pivot_type == "Curah Hujan Bulanan per Lokasi":
        st.subheader("🌧️ Pivot Table: Curah Hujan Bulanan per Lokasi")
        
        # Aggregation options
        agg_option = st.radio(
            "Pilih metode agregasi:",
            ["Rata-rata", "Maksimum", "Minimum"],
            horizontal=True
        )
        
        agg_func_map = {
            "Rata-rata": "mean",
            "Maksimum": "max",
            "Minimum": "min"
        }
        
        # Buat pivot table
        pivot_rainfall = df.pivot_table(
            values='curah_hujan_clean',
            index='lokasi_lengkap',
            columns='nama_bulan',
            aggfunc=agg_func_map[agg_option],
            fill_value=0
        ).round(2)
        
        # Urutkan kolom berdasarkan urutan bulan yang benar
        available_months = [month for month in month_order if month in pivot_rainfall.columns]
        pivot_rainfall = pivot_rainfall.reindex(columns=available_months)
        
        st.write(f"**{agg_option} Curah Hujan (mm) per Bulan dan Lokasi:**")
        st.dataframe(pivot_rainfall, use_container_width=True)
        
        # Download button
        csv = pivot_rainfall.to_csv()
        st.download_button(
            label="💾 Download CSV",
            data=csv,
            file_name=f"pivot_curah_hujan_{agg_option.lower()}.csv",
            mime="text/csv"
        )
        
        # Visualisasi heatmap
        fig_heatmap = px.imshow(
            pivot_rainfall,
            title=f"Heatmap: {agg_option} Curah Hujan Bulanan",
            color_continuous_scale="Blues",
            labels={'x': 'Bulan', 'y': 'Lokasi', 'color': f'Hujan (mm)'}
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    elif pivot_type == "Statistik Cuaca per Wilayah":
        st.subheader("🌤️ Pivot Table: Statistik Cuaca Komprehensif")
        
        # Multi-index pivot dengan berbagai variabel cuaca
        weather_stats = df.groupby('lokasi_lengkap').agg({
            'curah_hujan_clean': ['count', 'mean', 'max'],
            'suhu_rata': ['mean', 'min', 'max'],
            'kelembaban_rata': ['mean', 'min', 'max'],
            'kecepatan_angin_rata': ['mean', 'max']
        }).round(2)
        
        # Flatten column names
        weather_stats.columns = [
            'Hari Berdata', 'Hujan Rata-rata', 'Hujan Maks',
            'Suhu Rata-rata', 'Suhu Min', 'Suhu Max',
            'Kelembaban Rata-rata', 'Kelembaban Min', 'Kelembaban Max',
            'Angin Rata-rata', 'Angin Maksimum'
        ]
        
        st.write("**Statistik Cuaca Komprehensif per Wilayah:**")
        st.dataframe(weather_stats, use_container_width=True)
        
        # Download button
        csv = weather_stats.to_csv()
        st.download_button(
            label="💾 Download CSV",
            data=csv,
            file_name="pivot_statistik_cuaca.csv",
            mime="text/csv"
        )
        
        # Bar chart untuk perbandingan
        metric_to_plot = st.selectbox(
            "Pilih metrik untuk visualisasi:",
            weather_stats.columns.tolist()
        )
        
        fig_bar = px.bar(
            x=weather_stats.index,
            y=weather_stats[metric_to_plot],
            title=f"Perbandingan {metric_to_plot} Antar Wilayah",
            labels={'x': 'Lokasi', 'y': metric_to_plot}
        )
        fig_bar.update_xaxes(tickangle=45)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    elif pivot_type == "Analisis Musiman":
        st.subheader("🍂 Pivot Table: Analisis Musiman")
        
        # Definisi musim berdasarkan bulan (nama bulan dalam bahasa Inggris)
        def get_season(month):
            if month in ['December', 'January', 'February']:
                return 'Musim Hujan'
            elif month in ['March', 'April', 'May']:
                return 'Peralihan ke Kemarau'
            elif month in ['June', 'July', 'August']:
                return 'Musim Kemarau'
            else:
                return 'Peralihan ke Hujan'
        
        df_season = df.copy()
        df_season['musim'] = df_season['nama_bulan'].apply(get_season)
        
        variable_options = {
            "Curah Hujan": "curah_hujan_clean",
            "Suhu Rata-rata": "suhu_rata",
            "Kelembaban": "kelembaban_rata",
            "Kecepatan Angin": "kecepatan_angin_rata"
        }
        
        selected_var = st.selectbox("Pilih variabel untuk analisis musiman:", list(variable_options.keys()))
        
        seasonal_pivot = df_season.pivot_table(
            values=variable_options[selected_var],
            index='lokasi_lengkap',
            columns='musim',
            aggfunc='mean',
            fill_value=0
        ).round(2)
        
        # Reorder columns untuk urutan musim yang logis
        season_order = ['Musim Kemarau', 'Peralihan ke Hujan', 'Musim Hujan', 'Peralihan ke Kemarau']
        available_seasons = [season for season in season_order if season in seasonal_pivot.columns]
        seasonal_pivot = seasonal_pivot.reindex(columns=available_seasons)
        
        st.write(f"**Rata-rata {selected_var} per Musim:**")
        st.dataframe(seasonal_pivot, use_container_width=True)
        
        # Download button
        csv = seasonal_pivot.to_csv()
        st.download_button(
            label="💾 Download CSV",
            data=csv,
            file_name=f"pivot_musiman_{selected_var.lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )
        
        # Radar chart untuk analisis musiman
        fig_radar = go.Figure()
        
        # Gunakan warna konsisten
        _, location_colors = get_consistent_colors()
        
        for i, location in enumerate(seasonal_pivot.index):
            color = location_colors.get(location, px.colors.qualitative.Set2[i % len(px.colors.qualitative.Set2)])
            fig_radar.add_trace(go.Scatterpolar(
                r=seasonal_pivot.loc[location].values,
                theta=seasonal_pivot.columns,
                fill='toself',
                name=location,
                line_color=color
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True)
            ),
            showlegend=True,
            title=f"Perbandingan {selected_var} Antar Musim"
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    
    elif pivot_type == "Pivot Table Kustom":
        st.subheader("⚙️ Buat Pivot Table Kustom")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Pilih index (baris)
            index_options = ['lokasi_lengkap', 'nama_bulan', 'tahun', 'curah_hujan_kategori']
            selected_index = st.selectbox("Pilih Index (Baris):", index_options)
        
        with col2:
            # Pilih columns
            column_options = ['nama_bulan', 'tahun', 'lokasi_lengkap', 'curah_hujan_kategori']
            column_options = [col for col in column_options if col != selected_index]
            selected_columns = st.selectbox("Pilih Columns (Kolom):", column_options)
        
        with col3:
            # Pilih values dan aggregation
            value_options = {
                "Curah Hujan": "curah_hujan_clean",
                "Suhu Rata-rata": "suhu_rata", 
                "Suhu Minimum": "suhu_min",
                "Suhu Maksimum": "suhu_max",
                "Kelembaban": "kelembaban_rata",
                "Kecepatan Angin": "kecepatan_angin_rata"
            }
            selected_value = st.selectbox("Pilih Values:", list(value_options.keys()))
        
        # Pilih fungsi agregasi yang relevan untuk data cuaca
        agg_function = st.selectbox(
            "Pilih Fungsi Agregasi:",
            ["mean", "count", "max", "min", "std"],
            format_func=lambda x: {
                "mean": "Rata-rata",
                "count": "Jumlah",
                "max": "Maksimum", 
                "min": "Minimum",
                "std": "Standar Deviasi"
            }[x]
        )
        
        # Buat pivot table kustom
        try:
            custom_pivot = df.pivot_table(
                values=value_options[selected_value],
                index=selected_index,
                columns=selected_columns,
                aggfunc=agg_function,
                fill_value=0
            ).round(2)
            
            # Jika columns adalah nama_bulan, urutkan sesuai kalender
            if selected_columns == 'nama_bulan':
                available_months = [month for month in month_order if month in custom_pivot.columns]
                custom_pivot = custom_pivot.reindex(columns=available_months)
            
            st.write(f"**Pivot Table: {selected_value} per {selected_index} dan {selected_columns}**")
            st.dataframe(custom_pivot, use_container_width=True)
            
            # Download button
            csv = custom_pivot.to_csv()
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name=f"pivot_kustom_{selected_value.lower().replace(' ', '_')}.csv",
                mime="text/csv"
            )
            
            # Visualisasi otomatis jika ukuran data memungkinkan
            if custom_pivot.shape[0] <= 10 and custom_pivot.shape[1] <= 12:
                viz_type = st.radio("Pilih visualisasi:", ["Heatmap", "Bar Chart", "Line Chart"], horizontal=True)
                
                if viz_type == "Heatmap":
                    fig_custom = px.imshow(
                        custom_pivot,
                        title=f"Heatmap: {selected_value}",
                        color_continuous_scale="Viridis",
                        labels={'x': selected_columns, 'y': selected_index, 'color': selected_value}
                    )
                    st.plotly_chart(fig_custom, use_container_width=True)
                    
                elif viz_type == "Bar Chart":
                    # Ambil satu kolom untuk bar chart
                    if len(custom_pivot.columns) > 1:
                        selected_col = st.selectbox("Pilih kolom untuk Bar Chart:", custom_pivot.columns)
                        fig_custom = px.bar(
                            x=custom_pivot.index,
                            y=custom_pivot[selected_col],
                            title=f"Bar Chart: {selected_value} - {selected_col}",
                            labels={'x': selected_index, 'y': selected_value}
                        )
                    else:
                        fig_custom = px.bar(
                            x=custom_pivot.index,
                            y=custom_pivot.iloc[:, 0],
                            title=f"Bar Chart: {selected_value}",
                            labels={'x': selected_index, 'y': selected_value}
                        )
                    st.plotly_chart(fig_custom, use_container_width=True)
                    
                elif viz_type == "Line Chart":
                    custom_melted = custom_pivot.reset_index().melt(
                        id_vars=selected_index,
                        var_name=selected_columns,
                        value_name=selected_value
                    )
                    fig_custom = px.line(
                        custom_melted,
                        x=selected_columns,
                        y=selected_value,
                        color=selected_index,
                        title=f"Line Chart: {selected_value}",
                        markers=True
                    )
                    st.plotly_chart(fig_custom, use_container_width=True)
                    
        except Exception as e:
            st.error(f"Error dalam membuat pivot table: {str(e)}")
            st.info("Coba kombinasi index dan column yang berbeda")

if __name__ == "__main__":
    main()
