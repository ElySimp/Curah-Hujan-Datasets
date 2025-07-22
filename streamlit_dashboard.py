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
    page_title="BMKG Weather Data Dashboard",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

@st.cache_resource
def get_engine():
    """Create SQLAlchemy engine with connection pooling"""
    try:
        host = os.getenv('MYSQL_HOST')
        user = os.getenv('MYSQL_USER')
        password = os.getenv('MYSQL_PASSWORD')
        database = os.getenv('MYSQL_DATABASE')
        port = os.getenv('MYSQL_PORT', '3306')
        
        if not all([host, user, password, database]):
            st.error("❌ Environment variables are incomplete!")
            st.write(f"Host: {host}, User: {user}, Database: {database}, Port: {port}")
            return None
        
        connection_url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
        
        engine = create_engine(
            connection_url,
            pool_recycle=3600,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            connect_args={
                'connect_timeout': 10,
                'autocommit': True
            }
        )
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        return engine
        
    except Exception as e:
        st.error(f"❌ Failed to create database engine: {e}")
        return None

# Data loading functions
@st.cache_data(ttl=600)
def load_weather_data():
    """Load weather data from database using SQLAlchemy"""
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
            
        df = clean_weather_data(df)
        
        return df
        
    except Exception as e:
        return None

def clean_weather_data(df):
    """Clean weather data by handling special values"""
    df['rainfall_clean'] = df['curah_hujan'].apply(lambda x: 
        None if x in [8888, 9999] or pd.isna(x) else x)
    
    df['rainfall_category'] = df['rainfall_clean'].apply(categorize_rainfall)
    
    df['location_full'] = df['nama_lokasi'] + ' (' + df['jenis_lokasi'] + ')'
    
    df['date'] = pd.to_datetime(df['tanggal'])
    
    # Map Indonesian month names to English
    month_mapping = {
        'Januari': 'January',
        'Februari': 'February', 
        'Maret': 'March',
        'April': 'April',
        'Mei': 'May',
        'Juni': 'June',
        'Juli': 'July',
        'Agustus': 'August',
        'September': 'September',
        'Oktober': 'October',
        'November': 'November',
        'Desember': 'December'
    }
    
    df['month_name'] = df['nama_bulan'].map(month_mapping).fillna(df['nama_bulan'])
    df['year'] = df['tahun']
    
    return df

def categorize_rainfall(value):
    """Categorize rainfall intensity"""
    if pd.isna(value) or value is None:
        return 'No Data'
    elif value == 0:
        return 'No Rain'
    elif value <= 5:
        return 'Light Rain'
    elif value <= 20:
        return 'Moderate Rain'
    elif value <= 50:
        return 'Heavy Rain'
    else:
        return 'Very Heavy Rain'

def get_consistent_colors():
    """Return consistent color mapping for categories and locations"""
    rainfall_colors = {
        'No Data': '#d3d3d3',
        'No Rain': '#87ceeb',
        'Light Rain': '#90ee90',
        'Moderate Rain': '#ffd700',
        'Heavy Rain': '#ffa500',
        'Very Heavy Rain': '#ff4500'
    }
    
    location_colors = {
        'Bogor (Kabupaten)': '#1f77b4',
        'Bogor (Kota)': '#ff7f0e', 
        'Bandung (Kota)': '#2ca02c',
        'Cirebon (Kabupaten)': '#d62728',
        'Majalengka (Kabupaten)': '#9467bd'
    }
    
    return rainfall_colors, location_colors

def main():
    st.markdown('<h1 class="main-header">🌦️ BMKG West Java Weather Data Dashboard</h1>', unsafe_allow_html=True)
    
    with st.spinner('Loading weather data...'):
        df = load_weather_data()
    
    if df is None or df.empty:
        st.error("Data not available. Please check database connection and data.")
        return
    
    st.toast(f"✅ Data loaded: {len(df):,} records from {df['location_full'].nunique()} locations", icon="📊")

    st.sidebar.header("🔧 Filter Settings")
    
    if st.sidebar.button("🔄 Refresh Data", help="Click if data doesn't appear"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()
    
    all_locations = sorted(df['location_full'].unique().tolist())
    
    filter_mode = st.sidebar.radio(
        "Location Selection Mode:",
        ["Select All", "Select Multiple Locations", "Select One Location"]
    )
    
    if filter_mode == "Select All":
        selected_locations = all_locations
        st.sidebar.success(f"Showing all {len(all_locations)} locations")
    elif filter_mode == "Select Multiple Locations":
        selected_locations = st.sidebar.multiselect(
            "Select 2-4 locations to compare:",
            all_locations,
            default=all_locations[:3],
            help="Select maximum 4 locations for optimal comparison"
        )
        if len(selected_locations) > 4:
            st.sidebar.warning("⚠️ Maximum 4 locations for clear visualization")
            selected_locations = selected_locations[:4]
    else:
        selected_location = st.sidebar.selectbox("Select one location:", all_locations)
        selected_locations = [selected_location]
    
    min_date = df['tanggal'].min()
    max_date = df['tanggal'].max()
    date_range = st.sidebar.date_input(
        "Select Time Period:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Select date range for analysis"
    )
    
    filtered_df = df[df['location_full'].isin(selected_locations)].copy()
    
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['date'] >= pd.to_datetime(date_range[0])) &
            (filtered_df['date'] <= pd.to_datetime(date_range[1]))
        ]
    
    # Show active filter information
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📊 Active Filters:**")
    st.sidebar.write(f"• Locations: {len(selected_locations)} regions")
    st.sidebar.write(f"• Data: {len(filtered_df):,} days")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**👨‍💻 Created by:**")
    st.sidebar.markdown("**ElySimp's Team**")
    st.sidebar.markdown("- Faldo Maxwell")
    st.sidebar.markdown("- Michael Jeconiah Yonathan")
    st.sidebar.markdown("- Rafael Austin")
    st.sidebar.markdown("- Andhika Dwi Rachmawanto")
    st.sidebar.markdown("- Alfi Syahrian")
    st.sidebar.markdown("[📁 GitHub Repository](https://github.com/ElySimp/Curah-Hujan-Datasets)")
    st.sidebar.markdown("---")
    

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview", "🌧️ Rainfall Analysis", "🌡️ Temperature", "💨 Wind & Humidity", "📈 Time Series", "📋 Pivot Table"
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
    """Data overview tab"""
    st.subheader("📊 Weather Data Overview")
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_records = len(df)
        st.metric("Total Daily Data", f"{total_records:,}")
    
    with col2:
        unique_locations = df['location_full'].nunique()
        st.metric("Number of Regions", unique_locations)
    
    with col3:
        date_range = (df['date'].max() - df['date'].min()).days
        st.metric("Time Range (days)", date_range)
    
    with col4:
        avg_rainfall = df['rainfall_clean'].mean()
        st.metric("Average Daily Rainfall", f"{avg_rainfall:.1f} mm" if not pd.isna(avg_rainfall) else "No data")
    
    # Data quality
    st.subheader("📋 Data Completeness")
    
    col1, col2 = st.columns(2)
    
    with col1:
        missing_data = pd.DataFrame({
            'Data Type': ['Rainfall', 'Minimum Temperature', 'Maximum Temperature', 'Humidity', 'Wind Speed'],
            'Missing Data (%)': [
                (df['rainfall_clean'].isna().sum() / len(df)) * 100,
                (df['suhu_min'].isna().sum() / len(df)) * 100,
                (df['suhu_max'].isna().sum() / len(df)) * 100,
                (df['kelembaban_rata'].isna().sum() / len(df)) * 100,
                (df['kecepatan_angin_rata'].isna().sum() / len(df)) * 100
            ]
        })
        
        fig_missing = px.bar(missing_data, x='Data Type', y='Missing Data (%)', 
                           title="Percentage of Missing Data",
                           color='Missing Data (%)',
                           color_continuous_scale='Reds')
        fig_missing.update_layout(height=400)
        st.plotly_chart(fig_missing, use_container_width=True)
    
    with col2:
        location_counts = df.groupby('location_full').size().reset_index(name='Data_Count')
        fig_location = px.pie(location_counts, values='Data_Count', names='location_full',
                            title="Data Distribution by Region")
        fig_location.update_layout(height=400)
        st.plotly_chart(fig_location, use_container_width=True)

def rainfall_tab(df):
    """Rainfall analysis tab"""
    st.subheader("🌧️ Rainfall Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        rainfall_dist = df['rainfall_category'].value_counts()
        
        rainfall_colors, _ = get_consistent_colors()
        
        category_order = ['No Data', 'No Rain', 'Light Rain', 'Moderate Rain', 'Heavy Rain', 'Very Heavy Rain']
        
        rainfall_dist = rainfall_dist.reindex(category_order, fill_value=0)
        
        rainfall_dist = rainfall_dist[rainfall_dist > 0]
        
        colors = [rainfall_colors.get(category, '#cccccc') for category in rainfall_dist.index]
        
        fig_dist = px.pie(values=rainfall_dist.values, names=rainfall_dist.index,
                         title="Rainfall Intensity Distribution",
                         color_discrete_sequence=colors,
                         category_orders={"names": category_order})
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with col2:
        monthly_rainfall = df.groupby(['month_name', 'location_full'])['rainfall_clean'].mean().reset_index()
        
        location_colors = {
            'Bogor (Kabupaten)': '#1f77b4',
            'Bogor (Kota)': '#ff7f0e', 
            'Bandung (Kota)': '#2ca02c',
            'Cirebon (Kabupaten)': '#d62728',
            'Majalengka (Kabupaten)': '#9467bd'
        }
        
        fig_monthly = px.box(monthly_rainfall, x='month_name', y='rainfall_clean',
                           title="Rainfall Pattern Throughout the Year",
                           labels={'rainfall_clean': 'Rainfall (mm)', 'month_name': 'Month'})
        fig_monthly.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    st.subheader("📊 Rainfall Comparison Between Regions")
    
    location_rainfall = df.groupby('location_full').agg({
        'rainfall_clean': ['mean', 'sum', 'count']
    }).round(2)
    location_rainfall.columns = ['Daily Average (mm)', 'Total (mm)', 'Days with Data']
    
    st.dataframe(location_rainfall, use_container_width=True)
    
    if df['location_full'].nunique() > 1:
        st.subheader("🗓️ Monthly Rainfall Pattern by Region")
        
        month_order = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        
        pivot_rainfall = df.pivot_table(
            values='rainfall_clean', 
            index='location_full', 
            columns='month_name', 
            aggfunc='mean'
        )
        
        available_months = [month for month in month_order if month in pivot_rainfall.columns]
        pivot_rainfall = pivot_rainfall.reindex(columns=available_months)
        
        fig_heatmap = px.imshow(pivot_rainfall, 
                              title="Average Monthly Rainfall (mm)",
                              color_continuous_scale="Blues",
                              labels={'x': 'Month', 'y': 'Region', 'color': 'Rainfall (mm)'})
        st.plotly_chart(fig_heatmap, use_container_width=True)

def temperature_tab(df):
    """Temperature analysis tab"""
    st.subheader("🌡️ Temperature Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        temp_stats = df.groupby('location_full').agg({
            'suhu_min': 'mean',
            'suhu_max': 'mean',
            'suhu_rata': 'mean'
        }).round(1)
        
        _, location_colors = get_consistent_colors()
        
        fig_temp = go.Figure()
        
        for i, location in enumerate(temp_stats.index):
            color = location_colors.get(location, px.colors.qualitative.Set2[i % len(px.colors.qualitative.Set2)])
            fig_temp.add_trace(go.Scatter(
                x=['Minimum', 'Average', 'Maximum'],
                y=[temp_stats.loc[location, 'suhu_min'], 
                   temp_stats.loc[location, 'suhu_rata'],
                   temp_stats.loc[location, 'suhu_max']],
                mode='lines+markers',
                name=location,
                line=dict(width=3, color=color),
                marker=dict(size=8)
            ))
        
        fig_temp.update_layout(
            title="Average Temperature Profile by Region",
            xaxis_title="Temperature Type",
            yaxis_title="Temperature (°C)",
            height=400
        )
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with col2:
        temp_melted = pd.melt(df[['location_full', 'suhu_min', 'suhu_max', 'suhu_rata']], 
                            id_vars=['location_full'],
                            var_name='temp_type', value_name='temperature')
        
        temp_melted['temp_type'] = temp_melted['temp_type'].map({
            'suhu_min': 'Minimum',
            'suhu_max': 'Maximum', 
            'suhu_rata': 'Average'
        })
        
        fig_violin = px.violin(temp_melted, x='temp_type', y='temperature',
                             title="Temperature Distribution",
                             box=True,
                             labels={'temperature': 'Temperature (°C)', 'temp_type': 'Temperature Type'})
        st.plotly_chart(fig_violin, use_container_width=True)
    
    st.subheader("📈 Temperature Trends Throughout the Year")
    monthly_temp = df.groupby(['month_name', 'location_full']).agg({
        'suhu_min': 'mean',
        'suhu_max': 'mean',
        'suhu_rata': 'mean'
    }).reset_index()
    
    _, location_colors = get_consistent_colors()
    
    temp_type = st.selectbox(
        "Select temperature type:",
        ["suhu_rata", "suhu_min", "suhu_max"],
        format_func=lambda x: {"suhu_rata": "Average Temperature", "suhu_min": "Minimum Temperature", "suhu_max": "Maximum Temperature"}[x]
    )
    
    fig_monthly_temp = px.line(monthly_temp, x='month_name', y=temp_type,
                             color='location_full',
                             title=f"Monthly {temp_type.replace('_', ' ').title()} Trends",
                             labels={temp_type: 'Temperature (°C)', 'month_name': 'Month'},
                             markers=True,
                             color_discrete_map=location_colors)
    fig_monthly_temp.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_monthly_temp, use_container_width=True)

def wind_humidity_tab(df):
    """Wind and humidity analysis tab"""
    st.subheader("💨 Wind & Humidity Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_humidity = px.box(df, x='location_full', y='kelembaban_rata',
                            title="Humidity Levels by Region",
                            labels={'kelembaban_rata': 'Humidity (%)', 'location_full': 'Region'})
        fig_humidity.update_xaxes(tickangle=45)
        st.plotly_chart(fig_humidity, use_container_width=True)
    
    with col2:
        fig_wind = px.histogram(df, x='kecepatan_angin_rata', nbins=30,
                              title="Wind Speed Distribution",
                              labels={'kecepatan_angin_rata': 'Wind Speed (m/s)', 'count': 'Number of Days'})
        st.plotly_chart(fig_wind, use_container_width=True)
    
    st.subheader("📊 Inter-Regional Atmospheric Conditions Comparison")
    
    wind_humidity_stats = df.groupby('location_full').agg({
        'kelembaban_rata': ['mean', 'min', 'max'],
        'kecepatan_angin_rata': ['mean', 'min', 'max']
    }).round(2)
    
    wind_humidity_stats.columns = [
        'Average Humidity (%)', 'Min Humidity (%)', 'Max Humidity (%)',
        'Average Wind (m/s)', 'Min Wind (m/s)', 'Max Wind (m/s)'
    ]
    
    st.dataframe(wind_humidity_stats, use_container_width=True)
    
    if len(df) > 0:
        st.subheader("🌡️ Humidity and Temperature Relationship")
        
        _, location_colors = get_consistent_colors()
        
        fig_scatter = px.scatter(df, x='suhu_rata', y='kelembaban_rata', 
                               color='location_full',
                               title="Relationship between Temperature and Humidity",
                               labels={'suhu_rata': 'Average Temperature (°C)', 
                                      'kelembaban_rata': 'Humidity (%)'},
                               color_discrete_map=location_colors)
        st.plotly_chart(fig_scatter, use_container_width=True)

def timeseries_tab(df):
    """Time series analysis tab"""
    st.subheader("📈 Time Series Analysis")
    
    variables = {
        'Rainfall (mm)': 'rainfall_clean',
        'Average Temperature (°C)': 'suhu_rata',
        'Humidity (%)': 'kelembaban_rata',
        'Wind Speed (m/s)': 'kecepatan_angin_rata'
    }
    
    selected_var = st.selectbox("Select weather data:", list(variables.keys()))
    
    _, location_colors = get_consistent_colors()
    
    if df['location_full'].nunique() > 1:
        daily_data = df.groupby(['date', 'location_full'])[variables[selected_var]].mean().reset_index()
        
        fig_ts = px.line(daily_data, x='date', y=variables[selected_var],
                        color='location_full',
                        title=f"Daily Chart: {selected_var}",
                        labels={'date': 'Date', variables[selected_var]: selected_var},
                        color_discrete_map=location_colors)
        fig_ts.update_layout(height=500)
        st.plotly_chart(fig_ts, use_container_width=True)
    else:
        daily_data = df.groupby('date')[variables[selected_var]].mean().reset_index()
        
        fig_ts = px.line(daily_data, x='date', y=variables[selected_var],
                        title=f"Daily Chart: {selected_var}",
                        labels={'date': 'Date', variables[selected_var]: selected_var})
        fig_ts.update_layout(height=500)
        st.plotly_chart(fig_ts, use_container_width=True)
    
    st.subheader("📊 Moving Averages")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        window_size = st.slider("Average period (days):", 
                               min_value=3, max_value=30, value=7)
    
    ma_data = []
    for location in df['location_full'].unique():
        location_data = df[df['location_full'] == location].copy()
        location_data = location_data.sort_values('date')
        location_data[f'MA_{window_size}'] = location_data[variables[selected_var]].rolling(
            window=window_size, center=True).mean()
        ma_data.append(location_data)
    
    ma_df = pd.concat(ma_data)
    
    fig_ma = px.line(ma_df, x='date', y=f'MA_{window_size}',
                    color='location_full',
                    title=f"{selected_var} Trends ({window_size}-Day Average)",
                    labels={'date': 'Date', f'MA_{window_size}': f'{selected_var} (Average)'},
                    color_discrete_map=location_colors)
    fig_ma.update_layout(height=500)
    st.plotly_chart(fig_ma, use_container_width=True)

def pivot_table_tab(df):
    """Interactive pivot table analysis tab"""
    st.subheader("📋 Pivot Table Analysis")
    
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    pivot_type = st.selectbox(
        "Select pivot table analysis type:",
        [
            "Monthly Rainfall by Location",
            "Weather Statistics by Region",
            "Seasonal Analysis",
            "Custom Pivot Table"
        ]
    )
    
    if pivot_type == "Monthly Rainfall by Location":
        st.subheader("🌧️ Pivot Table: Monthly Rainfall by Location")
        
        agg_option = st.radio(
            "Select aggregation method:",
            ["Average", "Maximum", "Minimum"],
            horizontal=True
        )
        
        agg_func_map = {
            "Average": "mean",
            "Maximum": "max",
            "Minimum": "min"
        }
        
        pivot_rainfall = df.pivot_table(
            values='rainfall_clean',
            index='location_full',
            columns='month_name',
            aggfunc=agg_func_map[agg_option],
            fill_value=0
        ).round(2)
        
        available_months = [month for month in month_order if month in pivot_rainfall.columns]
        pivot_rainfall = pivot_rainfall.reindex(columns=available_months)
        
        st.write(f"**{agg_option} Rainfall (mm) by Month and Location:**")
        st.dataframe(pivot_rainfall, use_container_width=True)
        
        csv = pivot_rainfall.to_csv()
        st.download_button(
            label="💾 Download CSV",
            data=csv,
            file_name=f"pivot_rainfall_{agg_option.lower()}.csv",
            mime="text/csv"
        )
        
        fig_heatmap = px.imshow(
            pivot_rainfall,
            title=f"Heatmap: {agg_option} Monthly Rainfall",
            color_continuous_scale="Blues",
            labels={'x': 'Month', 'y': 'Location', 'color': f'Rainfall (mm)'}
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    elif pivot_type == "Weather Statistics by Region":
        st.subheader("🌤️ Pivot Table: Comprehensive Weather Statistics")
        
        weather_stats = df.groupby('location_full').agg({
            'rainfall_clean': ['count', 'mean', 'max'],
            'suhu_rata': ['mean', 'min', 'max'],
            'kelembaban_rata': ['mean', 'min', 'max'],
            'kecepatan_angin_rata': ['mean', 'max']
        }).round(2)
        
        weather_stats.columns = [
            'Days with Data', 'Average Rainfall', 'Max Rainfall',
            'Average Temperature', 'Min Temperature', 'Max Temperature',
            'Average Humidity', 'Min Humidity', 'Max Humidity',
            'Average Wind', 'Max Wind'
        ]
        
        st.write("**Comprehensive Weather Statistics by Region:**")
        st.dataframe(weather_stats, use_container_width=True)
        
        csv = weather_stats.to_csv()
        st.download_button(
            label="💾 Download CSV",
            data=csv,
            file_name="pivot_weather_statistics.csv",
            mime="text/csv"
        )
        
        metric_to_plot = st.selectbox(
            "Select metric for visualization:",
            weather_stats.columns.tolist()
        )
        
        fig_bar = px.bar(
            x=weather_stats.index,
            y=weather_stats[metric_to_plot],
            title=f"Comparison of {metric_to_plot} Across Regions",
            labels={'x': 'Location', 'y': metric_to_plot}
        )
        fig_bar.update_xaxes(tickangle=45)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    elif pivot_type == "Seasonal Analysis":
        st.subheader("🍂 Pivot Table: Seasonal Analysis")
        
        def get_season(month):
            if month in ['December', 'January', 'February']:
                return 'Rainy Season'
            elif month in ['March', 'April', 'May']:
                return 'Transition to Dry'
            elif month in ['June', 'July', 'August']:
                return 'Dry Season'
            else:
                return 'Transition to Rainy'
        
        df_season = df.copy()
        df_season['musim'] = df_season['month_name'].apply(get_season)
        
        variable_options = {
            "Rainfall": "rainfall_clean",
            "Average Temperature": "suhu_rata",
            "Humidity": "kelembaban_rata",
            "Wind Speed": "kecepatan_angin_rata"
        }
        
        selected_var = st.selectbox("Select variable for seasonal analysis:", list(variable_options.keys()))
        
        seasonal_pivot = df_season.pivot_table(
            values=variable_options[selected_var],
            index='location_full',
            columns='musim',
            aggfunc='mean',
            fill_value=0
        ).round(2)
        
        season_order = ['Dry Season', 'Transition to Rainy', 'Rainy Season', 'Transition to Dry']
        available_seasons = [season for season in season_order if season in seasonal_pivot.columns]
        seasonal_pivot = seasonal_pivot.reindex(columns=available_seasons)
        
        st.write(f"**Average {selected_var} per Season:**")
        st.dataframe(seasonal_pivot, use_container_width=True)
        
        csv = seasonal_pivot.to_csv()
        st.download_button(
            label="💾 Download CSV",
            data=csv,
            file_name=f"pivot_seasonal_{selected_var.lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )
        
        fig_radar = go.Figure()
        
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
            title=f"Comparison of {selected_var} Across Seasons"
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    
    elif pivot_type == "Custom Pivot Table":
        st.subheader("⚙️ Create Custom Pivot Table")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            index_options = ['location_full', 'month_name', 'year', 'rainfall_category']
            selected_index = st.selectbox("Select Index (Rows):", index_options)
        
        with col2:
            column_options = ['month_name', 'year', 'location_full', 'rainfall_category']
            column_options = [col for col in column_options if col != selected_index]
            selected_columns = st.selectbox("Select Columns:", column_options)
        
        with col3:
            value_options = {
                "Rainfall": "rainfall_clean",
                "Average Temperature": "suhu_rata", 
                "Minimum Temperature": "suhu_min",
                "Maximum Temperature": "suhu_max",
                "Humidity": "kelembaban_rata",
                "Wind Speed": "kecepatan_angin_rata"
            }
            selected_value = st.selectbox("Select Values:", list(value_options.keys()))
        
        agg_function = st.selectbox(
            "Select Aggregation Function:",
            ["mean", "count", "max", "min", "std"],
            format_func=lambda x: {
                "mean": "Average",
                "count": "Count",
                "max": "Maximum", 
                "min": "Minimum",
                "std": "Standard Deviation"
            }[x]
        )
        
        try:
            custom_pivot = df.pivot_table(
                values=value_options[selected_value],
                index=selected_index,
                columns=selected_columns,
                aggfunc=agg_function,
                fill_value=0
            ).round(2)
            
            if selected_columns == 'month_name':
                available_months = [month for month in month_order if month in custom_pivot.columns]
                custom_pivot = custom_pivot.reindex(columns=available_months)
            
            st.write(f"**Pivot Table: {selected_value} by {selected_index} and {selected_columns}**")
            st.dataframe(custom_pivot, use_container_width=True)
            
            csv = custom_pivot.to_csv()
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name=f"pivot_custom_{selected_value.lower().replace(' ', '_')}.csv",
                mime="text/csv"
            )
            
            if custom_pivot.shape[0] <= 10 and custom_pivot.shape[1] <= 12:
                viz_type = st.radio("Select visualization:", ["Heatmap", "Bar Chart", "Line Chart"], horizontal=True)
                
                if viz_type == "Heatmap":
                    fig_custom = px.imshow(
                        custom_pivot,
                        title=f"Heatmap: {selected_value}",
                        color_continuous_scale="Viridis",
                        labels={'x': selected_columns, 'y': selected_index, 'color': selected_value}
                    )
                    st.plotly_chart(fig_custom, use_container_width=True)
                    
                elif viz_type == "Bar Chart":
                    if len(custom_pivot.columns) > 1:
                        selected_col = st.selectbox("Select column for Bar Chart:", custom_pivot.columns)
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
            st.error(f"Error creating pivot table: {str(e)}")
            st.info("Try different combinations of index and columns")

if __name__ == "__main__":
    main()