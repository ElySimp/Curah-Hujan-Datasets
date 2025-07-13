import streamlit as st
import pandas as pd
import mysql.connector
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
    page_title="BMKG Weather Data Dashboard",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #e8f4f8;
    }
</style>
""", unsafe_allow_html=True)

# Database connection
@st.cache_resource
def init_connection():
    """Initialize database connection"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE'),
            port=int(os.getenv('MYSQL_PORT'))
        )
        return connection
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# Data loading functions
@st.cache_data(ttl=600)
def load_weather_data():
    """Load weather data from database"""
    conn = init_connection()
    if conn is None:
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
        df = pd.read_sql(query, conn)
        conn.close()
        
        # Data cleaning
        df = clean_weather_data(df)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def clean_weather_data(df):
    """Clean weather data by handling special values"""
    # Handle rainfall special codes
    df['curah_hujan_clean'] = df['curah_hujan'].apply(lambda x: 
        None if x in [8888, 9999] or pd.isna(x) else x)
    
    # Create rainfall categories
    df['curah_hujan_kategori'] = df['curah_hujan_clean'].apply(categorize_rainfall)
    
    # Create full location name
    df['lokasi_lengkap'] = df['nama_lokasi'] + ' (' + df['jenis_lokasi'] + ')'
    
    # Convert date column
    df['tanggal'] = pd.to_datetime(df['tanggal'])
    
    return df

def categorize_rainfall(value):
    """Categorize rainfall intensity"""
    if pd.isna(value) or value is None:
        return 'No Data'
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

# Main dashboard
def main():
    st.markdown('<h1 class="main-header">🌦️ BMKG Weather Data Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner('Loading weather data...'):
        df = load_weather_data()
    
    if df is None or df.empty:
        st.error("No data available. Please check your database connection and data.")
        return
    
    # Sidebar filters
    st.sidebar.header("📊 Filter Data")
    
    # Location filter
    locations = ['All'] + sorted(df['lokasi_lengkap'].unique().tolist())
    selected_location = st.sidebar.selectbox("Pilih Lokasi:", locations)
    
    # Date range filter
    min_date = df['tanggal'].min()
    max_date = df['tanggal'].max()
    date_range = st.sidebar.date_input(
        "Pilih Rentang Tanggal:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Filter data
    filtered_df = df.copy()
    if selected_location != 'All':
        filtered_df = filtered_df[filtered_df['lokasi_lengkap'] == selected_location]
    
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['tanggal'] >= pd.to_datetime(date_range[0])) &
            (filtered_df['tanggal'] <= pd.to_datetime(date_range[1]))
        ]
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview", "🌧️ Rainfall Analysis", "🌡️ Temperature", "💨 Wind & Humidity", "📅 Time Series"
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
    """Overview dashboard tab"""
    st.subheader("📊 Data Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_records = len(df)
        st.metric("Total Records", f"{total_records:,}")
    
    with col2:
        unique_locations = df['lokasi_lengkap'].nunique()
        st.metric("Locations", unique_locations)
    
    with col3:
        date_range = (df['tanggal'].max() - df['tanggal'].min()).days
        st.metric("Date Range (days)", date_range)
    
    with col4:
        avg_rainfall = df['curah_hujan_clean'].mean()
        st.metric("Avg Rainfall (mm)", f"{avg_rainfall:.1f}" if not pd.isna(avg_rainfall) else "N/A")
    
    # Data quality overview
    st.subheader("📋 Data Quality Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Missing data summary
        missing_data = pd.DataFrame({
            'Column': ['Curah Hujan', 'Suhu Min', 'Suhu Max', 'Kelembaban', 'Kec. Angin'],
            'Missing %': [
                (df['curah_hujan_clean'].isna().sum() / len(df)) * 100,
                (df['suhu_min'].isna().sum() / len(df)) * 100,
                (df['suhu_max'].isna().sum() / len(df)) * 100,
                (df['kelembaban_rata'].isna().sum() / len(df)) * 100,
                (df['kecepatan_angin_rata'].isna().sum() / len(df)) * 100
            ]
        })
        
        fig_missing = px.bar(missing_data, x='Column', y='Missing %', 
                           title="Percentage of Missing Data by Variable")
        fig_missing.update_layout(height=400)
        st.plotly_chart(fig_missing, use_container_width=True)
    
    with col2:
        # Records per location
        location_counts = df.groupby('lokasi_lengkap').size().reset_index(name='Records')
        fig_location = px.pie(location_counts, values='Records', names='lokasi_lengkap',
                            title="Data Distribution by Location")
        fig_location.update_layout(height=400)
        st.plotly_chart(fig_location, use_container_width=True)

def rainfall_tab(df):
    """Rainfall analysis tab"""
    st.subheader("🌧️ Rainfall Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Rainfall distribution by category
        rainfall_dist = df['curah_hujan_kategori'].value_counts()
        fig_dist = px.pie(values=rainfall_dist.values, names=rainfall_dist.index,
                         title="Rainfall Distribution by Category")
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with col2:
        # Monthly rainfall comparison
        monthly_rainfall = df.groupby(['nama_bulan', 'lokasi_lengkap'])['curah_hujan_clean'].mean().reset_index()
        fig_monthly = px.box(monthly_rainfall, x='nama_bulan', y='curah_hujan_clean',
                           title="Monthly Rainfall Distribution")
        fig_monthly.update_xaxes(title="Month")
        fig_monthly.update_yaxes(title="Rainfall (mm)")
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    # Rainfall by location comparison
    st.subheader("Rainfall Comparison by Location")
    location_rainfall = df.groupby('lokasi_lengkap').agg({
        'curah_hujan_clean': ['mean', 'sum', 'count']
    }).round(2)
    location_rainfall.columns = ['Average (mm)', 'Total (mm)', 'Days with Data']
    st.dataframe(location_rainfall)
    
    # Heatmap of rainfall by month and location
    if df['lokasi_lengkap'].nunique() > 1:
        pivot_rainfall = df.pivot_table(
            values='curah_hujan_clean', 
            index='lokasi_lengkap', 
            columns='nama_bulan', 
            aggfunc='mean'
        )
        
        fig_heatmap = px.imshow(pivot_rainfall, 
                              title="Average Monthly Rainfall by Location (mm)",
                              color_continuous_scale="Blues")
        st.plotly_chart(fig_heatmap, use_container_width=True)

def temperature_tab(df):
    """Temperature analysis tab"""
    st.subheader("🌡️ Temperature Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Temperature range by location
        temp_stats = df.groupby('lokasi_lengkap').agg({
            'suhu_min': 'mean',
            'suhu_max': 'mean',
            'suhu_rata': 'mean'
        }).round(1)
        
        fig_temp = go.Figure()
        for location in temp_stats.index:
            fig_temp.add_trace(go.Scatter(
                x=['Min', 'Average', 'Max'],
                y=[temp_stats.loc[location, 'suhu_min'], 
                   temp_stats.loc[location, 'suhu_rata'],
                   temp_stats.loc[location, 'suhu_max']],
                mode='lines+markers',
                name=location,
                line=dict(width=3)
            ))
        
        fig_temp.update_layout(
            title="Average Temperature Range by Location",
            xaxis_title="Temperature Type",
            yaxis_title="Temperature (°C)",
            height=400
        )
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with col2:
        # Temperature distribution
        temp_melted = pd.melt(df[['lokasi_lengkap', 'suhu_min', 'suhu_max', 'suhu_rata']], 
                            id_vars=['lokasi_lengkap'],
                            var_name='temp_type', value_name='temperature')
        
        fig_violin = px.violin(temp_melted, x='temp_type', y='temperature',
                             title="Temperature Distribution",
                             box=True)
        fig_violin.update_xaxes(title="Temperature Type")
        fig_violin.update_yaxes(title="Temperature (°C)")
        st.plotly_chart(fig_violin, use_container_width=True)
    
    # Monthly temperature trends
    monthly_temp = df.groupby(['nama_bulan', 'lokasi_lengkap']).agg({
        'suhu_min': 'mean',
        'suhu_max': 'mean',
        'suhu_rata': 'mean'
    }).reset_index()
    
    fig_monthly_temp = px.line(monthly_temp, x='nama_bulan', y='suhu_rata',
                             color='lokasi_lengkap',
                             title="Monthly Average Temperature Trends")
    fig_monthly_temp.update_xaxes(title="Month")
    fig_monthly_temp.update_yaxes(title="Average Temperature (°C)")
    st.plotly_chart(fig_monthly_temp, use_container_width=True)

def wind_humidity_tab(df):
    """Wind and humidity analysis tab"""
    st.subheader("💨 Wind & Humidity Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Humidity distribution
        fig_humidity = px.box(df, x='lokasi_lengkap', y='kelembaban_rata',
                            title="Humidity Distribution by Location")
        fig_humidity.update_xaxes(title="Location", tickangle=45)
        fig_humidity.update_yaxes(title="Humidity (%)")
        st.plotly_chart(fig_humidity, use_container_width=True)
    
    with col2:
        # Wind speed distribution
        fig_wind = px.histogram(df, x='kecepatan_angin_rata', nbins=30,
                              title="Wind Speed Distribution")
        fig_wind.update_xaxes(title="Wind Speed (m/s)")
        fig_wind.update_yaxes(title="Frequency")
        st.plotly_chart(fig_wind, use_container_width=True)
    
    # Correlation analysis
    st.subheader("🔗 Weather Variables Correlation")
    
    # Select numeric columns for correlation
    numeric_cols = ['curah_hujan_clean', 'suhu_min', 'suhu_max', 'suhu_rata', 
                   'kelembaban_rata', 'kecepatan_angin_rata', 'lama_penyinaran']
    
    corr_df = df[numeric_cols].corr()
    
    fig_corr = px.imshow(corr_df, 
                        title="Correlation Matrix of Weather Variables",
                        color_continuous_scale="RdBu_r",
                        aspect="auto")
    st.plotly_chart(fig_corr, use_container_width=True)

def timeseries_tab(df):
    """Time series analysis tab"""
    st.subheader("📅 Time Series Analysis")
    
    # Variable selection for time series
    variables = {
        'Curah Hujan': 'curah_hujan_clean',
        'Suhu Rata-rata': 'suhu_rata',
        'Kelembaban': 'kelembaban_rata',
        'Kecepatan Angin': 'kecepatan_angin_rata'
    }
    
    selected_var = st.selectbox("Pilih variabel untuk analisis time series:", 
                               list(variables.keys()))
    
    # Time series plot
    if df['lokasi_lengkap'].nunique() > 1:
        daily_data = df.groupby(['tanggal', 'lokasi_lengkap'])[variables[selected_var]].mean().reset_index()
        
        fig_ts = px.line(daily_data, x='tanggal', y=variables[selected_var],
                        color='lokasi_lengkap',
                        title=f"Daily {selected_var} Time Series")
        fig_ts.update_xaxes(title="Date")
        fig_ts.update_yaxes(title=selected_var)
        st.plotly_chart(fig_ts, use_container_width=True)
    else:
        daily_data = df.groupby('tanggal')[variables[selected_var]].mean().reset_index()
        
        fig_ts = px.line(daily_data, x='tanggal', y=variables[selected_var],
                        title=f"Daily {selected_var} Time Series")
        fig_ts.update_xaxes(title="Date")
        fig_ts.update_yaxes(title=selected_var)
        st.plotly_chart(fig_ts, use_container_width=True)
    
    # Moving averages
    st.subheader("📈 Moving Averages")
    
    col1, col2 = st.columns(2)
    
    with col1:
        window_size = st.slider("Moving Average Window (days):", 
                               min_value=3, max_value=30, value=7)
    
    # Calculate moving averages for each location
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
                    title=f"{window_size}-Day Moving Average of {selected_var}")
    fig_ma.update_xaxes(title="Date")
    fig_ma.update_yaxes(title=f"{selected_var} (Moving Average)")
    st.plotly_chart(fig_ma, use_container_width=True)

if __name__ == "__main__":
    main()
