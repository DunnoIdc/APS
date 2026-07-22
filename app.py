# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import altair as alt
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(
    page_title="Pemetaan Zona Rawan Banjir Kota Sorong",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&family=Sora:wght@700;800&display=swap');

*, html, body { margin: 0; padding: 0; box-sizing: border-box; }
.stApp { background-color: #f8fafc !important; font-family: 'Inter', sans-serif; }

/* Force dark text for general elements inside the app to prevent light text on light backgrounds in Dark Mode */
.stApp p, 
.stApp label, 
.stApp span, 
.stApp li, 
.stApp td, 
.stApp th,
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stWidgetLabel"] label,
.stApp div[role="radiogroup"] label {
    color: #1e293b !important;
}

.stApp h1, 
.stApp h2, 
.stApp h3, 
.stApp h4, 
.stApp h5, 
.stApp h6 {
    color: #0f172a !important;
}

/* Force Streamlit app view to take full screen width and remove padding */
header[data-testid="stHeader"] {
    display: none !important;
}
.block-container, [data-testid="stAppViewBlockContainer"] {
    padding: 0px !important;
}

/* Pad the tab container content so it does not touch the window edges */
div[data-testid="stTabs"] {
    padding-left: 3rem !important;
    padding-right: 3rem !important;
}

.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0369a1 100%);
    padding: 60px 3rem;
    margin: 0px 0px 40px 0px;
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: '';
    position: absolute;
    inset: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}
.hero-inner { position: relative; z-index: 1; max-width: 1000px; }
.hero-tag {
    display: inline-block;
    background: rgba(239, 68, 68, 0.2);
    border: 1px solid rgba(239, 68, 68, 0.4);
    color: #fca5a5;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 5px 14px;
    border-radius: 999px;
    margin-bottom: 18px;
}
.stApp .hero h1, .stApp .hero-inner h1 {
    font-family: 'Sora', sans-serif;
    font-size: 3.0rem;
    font-weight: 800;
    color: #ffffff !important;
    line-height: 1.15;
    margin-bottom: 14px;
}
.stApp .hero p, .stApp .hero-inner p, .stApp .hero-inner [data-testid="stMarkdownContainer"] p {
    font-size: 1.1rem;
    color: rgba(255,255,255,0.85) !important;
    max-width: 750px;
    line-height: 1.7;
}
.stApp .hero-tag, .stApp .hero-inner .hero-tag {
    color: #fca5a5 !important;
}
.stApp .hero-stats, .stApp .hero-inner .hero-stats {
    display: flex;
    gap: 35px;
    margin-top: 30px;
    flex-wrap: wrap;
}
.stApp .hero-stat { color: white !important; }
.stApp .hero-stat .val {
    font-family: 'Sora', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    line-height: 1;
    color: #ffffff !important;
}
.stApp .hero-stat .lbl {
    font-size: 0.78rem;
    color: rgba(255,255,255,0.65) !important;
    margin-top: 3px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.section-title {
    font-family: 'Sora', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 6px;
}
.section-sub {
    font-size: 0.9rem;
    color: #64748b;
    margin-bottom: 24px;
}

.card {
    background: #ffffff;
    border-radius: 20px;
    padding: 28px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 18px rgba(15, 23, 42, 0.03);
    margin-bottom: 24px;
}

.band-row {
    display: flex;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #f1f5f9;
    gap: 12px;
    font-size: 0.9rem;
    color: #334155;
}
.band-dot {
    width: 12px; height: 12px;
    border-radius: 3px;
    flex-shrink: 0;
}
.band-name { flex: 1; font-weight: 600; }
.band-val { color: #1e3a8a; font-weight: 700; font-size: 0.95rem; }
.band-pct { color: #94a3b8; font-size: 0.82rem; width: 50px; text-align: right; }

.insight-box {
    background: linear-gradient(135deg, #f0f9ff, #f8fafc);
    border-left: 5px solid #0284c7;
    border-radius: 8px;
    padding: 18px 22px;
    margin-bottom: 18px;
    font-size: 0.92rem;
    color: #1e293b;
    line-height: 1.65;
    box-shadow: 0 2px 8px rgba(0,0,0,0.01);
}
.insight-box-warn {
    background: linear-gradient(135deg, #fef2f2, #f8fafc);
    border-left: 5px solid #ef4444;
    border-radius: 8px;
    padding: 18px 22px;
    margin-bottom: 18px;
    font-size: 0.92rem;
    color: #1e293b;
    line-height: 1.65;
    box-shadow: 0 2px 8px rgba(0,0,0,0.01);
}
.insight-box-suggest {
    background: linear-gradient(135deg, #f0fdf4, #f8fafc);
    border-left: 5px solid #22c55e;
    border-radius: 8px;
    padding: 18px 22px;
    margin-bottom: 18px;
    font-size: 0.92rem;
    color: #1e293b;
    line-height: 1.65;
    box-shadow: 0 2px 8px rgba(0,0,0,0.01);
}

.stApp .footer {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    padding: 35px 3rem;
    margin: 40px 0px 0px 0px;
    border-top: 3px solid #3b82f6;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 20px;
    color: white !important;
}
.stApp .footer h4 {
    font-family: 'Sora', sans-serif;
    font-size: 1.2rem;
    margin: 0 0 6px 0;
    color: #3b82f6 !important;
}
.stApp .footer p, .stApp .footer [data-testid="stMarkdownContainer"] p { font-size: 0.82rem; color: rgba(255,255,255,0.55) !important; margin: 0; }
.stApp .footer span { color: rgba(255,255,255,0.55) !important; }
.stApp .footer-badge {
    background: rgba(59, 130, 246, 0.2);
    border: 1px solid #3b82f6;
    color: #60a5fa !important;
    padding: 5px 14px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    display: block;
    margin-bottom: 8px;
    text-align: right;
}
.stApp .footer-names { font-size: 0.75rem; color: rgba(255,255,255,0.4) !important; text-align: right; }

section[data-testid="stSidebar"] { background: #0f172a !important; }

/* Custom style for Streamlit container with border=True to look like a premium card */
div[data-testid="stVerticalBlockBorderedTest"] {
    background: #ffffff !important;
    border-radius: 20px !important;
    padding: 28px !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 4px 18px rgba(15, 23, 42, 0.03) !important;
    margin-bottom: 24px !important;
}
/* Force dark text for readability on white card background in both light/dark modes */
div[data-testid="stVerticalBlockBorderedTest"] p,
div[data-testid="stVerticalBlockBorderedTest"] label,
div[data-testid="stVerticalBlockBorderedTest"] span,
div[data-testid="stVerticalBlockBorderedTest"] div,
div[data-testid="stVerticalBlockBorderedTest"] h3,
div[data-testid="stVerticalBlockBorderedTest"] h4 {
    color: #1e293b !important;
}

/* Make tabs stretch evenly across the page width */
div[role="tablist"] {
    display: flex !important;
    width: 100% !important;
    gap: 8px !important;
}
button[role="tab"], button[data-baseweb="tab"] {
    flex: 1 !important;
    text-align: center !important;
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease-in-out !important;
}
button[role="tab"] p, button[data-baseweb="tab"] p,
button[role="tab"] span, button[data-baseweb="tab"] span {
    color: #475569 !important;
    font-weight: 600 !important;
}
button[role="tab"]:hover, button[data-baseweb="tab"]:hover {
    border-color: #93c5fd !important;
    background-color: #eff6ff !important;
}
button[role="tab"]:hover p, button[data-baseweb="tab"]:hover p,
button[role="tab"]:hover span, button[data-baseweb="tab"]:hover span {
    color: #2563eb !important;
}
button[role="tab"][aria-selected="true"], button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    border-color: #2563eb !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15) !important;
}
button[role="tab"][aria-selected="true"] p, button[data-baseweb="tab"][aria-selected="true"] p,
button[role="tab"][aria-selected="true"] span, button[data-baseweb="tab"][aria-selected="true"] span {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA & CALCULATIONS ──────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data_spasial.csv.gz", compression="gzip")
    
    # Scoring Elevation (Lower is higher risk) - Based on Floodplain Morphometry & Tidal Limit
    def score_elevation(elev):
        if elev <= 2: return 5      # Sangat Rawan (Pasang surut/rob pantai)
        elif elev <= 5: return 4    # Rawan (Dataran banjir sungai aktif)
        elif elev <= 10: return 3   # Cukup Rawan (Dataran rendah transisi)
        elif elev <= 15: return 2   # Aman (Kaki perbukitan aman)
        else: return 1              # Sangat Aman (Perbukitan tinggi)
        
    # Scoring Slope (Flatter is higher risk) - Based on Van Zuidam (1985) Relief Classification
    def score_slope(slope):
        if slope <= 1: return 5     # Datar
        elif slope <= 2: return 4   # Sangat Landai
        elif slope <= 5: return 3   # Landai
        elif slope <= 10: return 2  # Agak Curam
        else: return 1              # Curam
        
    # Scoring Land Cover - Based on SNI 2415:2016 Runoff Coefficients (C)
    lc_scores = {
        'PERMUKIMAN': 5,            # Kedap air (C = 0.70 - 0.95)
        'LADANG': 4,                # Pertanian lahan kering (C = 0.50 - 0.60)
        'TANAMAN CAMPUR': 4,        # Kebun campuran (C = 0.50 - 0.60)
        'PENUTUP LAHAN': 3,         # Lahan terbuka vegetasi rendah (C = 0.20 - 0.40)
        'HERBA DAN RUMPUT': 3,      # Padang rumput (C = 0.20 - 0.40)
        'SEMAK BELUKAR': 2,         # Vegetasi sedang (C = 0.15 - 0.30)
        'HUTAN LAHAN RENDAH': 1,    # Vegetasi rapat/infiltrasi tinggi (C = 0.05 - 0.20)
        'HUTAN LAHAN TINGGI': 1,
        'HUTAN MANGROVE': 1
    }
    
    df['score_el'] = df['elevation'].apply(score_elevation)
    df['score_sl'] = df['slope'].apply(score_slope)
    df['score_lc'] = df['clean_layer'].map(lc_scores).fillna(3)
    
    # Weighted overlay (Elevation 60%, Slope 30%, Land Cover 10% - AHP Method)
    df['fvi'] = 0.60 * df['score_el'] + 0.30 * df['score_sl'] + 0.10 * df['score_lc']
    
    # Classify vulnerability classes - Strict Geometrical Breaks
    def classify_fvi(v):
        if v <= 2.5: return "Sangat Aman"
        elif v <= 3.2: return "Aman"
        elif v <= 4.0: return "Cukup Rawan"
        elif v <= 4.6: return "Rawan"
        else: return "Sangat Rawan"
        
    df['flood_class'] = df['fvi'].apply(classify_fvi)
    
    # Map colors for DeckGL/Pydeck representation [R, G, B, A]
    class_colors = {
        'Sangat Aman': [16, 185, 129, 200],  # #10b981
        'Aman': [132, 204, 22, 200],         # #84cc16
        'Cukup Rawan': [234, 179, 8, 200],    # #eab308
        'Rawan': [249, 115, 22, 200],         # #f97316
        'Sangat Rawan': [239, 68, 68, 200]    # #ef4444
    }
    df['color_fvi'] = df['flood_class'].map(class_colors)
    
    return df

@st.cache_data
def load_geo():
    if os.path.exists("tutupan_lahan.geojson"):
        gdf = gpd.read_file("tutupan_lahan.geojson")
        if gdf is not None and not gdf.empty:
            gdf['geom_area'] = gdf.geometry.area
            gdf = gdf.sort_values(by='geom_area', ascending=False).drop(columns=['geom_area'])
        return gdf
    return None

df = load_data()
gdf = load_geo()

# Global statistics
total = len(df)
px_ha = 4.3316
area_total = total * px_ha

fvi_counts = df['flood_class'].value_counts()
rawan_sangat_rawan_count = fvi_counts.get('Rawan', 0) + fvi_counts.get('Sangat Rawan', 0)
pct_rawan_sangat_rawan = (rawan_sangat_rawan_count / total) * 100
area_rawan_sangat_rawan = rawan_sangat_rawan_count * px_ha

# Settlement vulnerability
permukiman_total = len(df[df['clean_layer'] == 'PERMUKIMAN'])
permukiman_rawan = len(df[(df['clean_layer'] == 'PERMUKIMAN') & (df['flood_class'].isin(['Rawan', 'Sangat Rawan']))])
pct_permukiman_rawan = (permukiman_rawan / permukiman_total * 100) if permukiman_total > 0 else 0
area_permukiman_rawan = permukiman_rawan * px_ha

lc_palette = {
    'HUTAN LAHAN RENDAH': '#15803d',
    'HUTAN LAHAN TINGGI': '#14532d',
    'HUTAN MANGROVE': '#0d9488',
    'SEMAK BELUKAR': '#65a30d',
    'HERBA DAN RUMPUT': '#a3e635',
    'TANAMAN CAMPUR': '#d97706',
    'LADANG': '#f59e0b',
    'PERKEBUNAN': '#10b981',
    'PERMUKIMAN': '#dc2626',
    'PENUTUP LAHAN': '#94a3b8',
}

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <div class="hero-inner">
    <div class="hero-tag">⚠️ GIS Risk Assessment Platform</div>
    <h1>Pemetaan Zona Rawan Banjir Kota Sorong<br>Berbasis Data DEM dan Tutupan Lahan</h1>
    <p>Aplikasi Geospasial interaktif untuk memetakan dan menganalisis tingkat kerawanan banjir di wilayah Kota Sorong, Papua Barat Daya.
       Penentuan tingkat kerawanan dihitung melalui metode pembobotan (Weighted Overlay) berdasarkan parameter Elevasi (DEM SRTM), Kemiringan Lereng (Slope), dan Koefisien Limpasan Tutupan Lahan (BIG).</p>
    <div class="hero-stats">
      <div class="hero-stat">
        <div class="val">{area_total:,.0f} Ha</div>
        <div class="lbl">Hektar Terpetakan</div>
      </div>
      <div class="hero-stat">
        <div class="val">{pct_rawan_sangat_rawan:.1f}%</div>
        <div class="lbl">Zona Rawan &amp; Sangat Rawan</div>
      </div>
      <div class="hero-stat">
        <div class="val">{area_rawan_sangat_rawan:,.0f} Ha</div>
        <div class="lbl">Luas Zona Berisiko</div>
      </div>
      <div class="hero-stat">
        <div class="val">{pct_permukiman_rawan:.1f}%</div>
        <div class="lbl">Permukiman Terdampak</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "⚠️ Peta Kerawanan Banjir (3D)",
    "🗺️ Peta Parameter Geografis (2D)",
    "📊 Statistik & Hubungan Spasial",
    "💡 Analisis & Mitigasi Bencana"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PETA KERAWANAN BANJIR (3D)
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">⚠️ Peta Interaktif Kerawanan Banjir (3D Deck.GL)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Visualisasi 3D tingkat kerawanan banjir hasil overlay parameter DEM & Tutupan Lahan di Kota Sorong</div>', unsafe_allow_html=True)

    col_map, col_ctrl = st.columns([2.2, 1])

    with col_ctrl:
        with st.container(border=True):
            st.markdown("**🎨 Warnai Peta Berdasarkan:**")
            color_by = st.radio("", ["Tingkat Kerawanan Banjir", "Ketinggian (Elevasi)", "Kemiringan (Slope)", "Tutupan Lahan"], label_visibility="collapsed")
            st.markdown("---")
            st.markdown("**📐 Skala Tinggi Kolom Elevasi:**")
            elev_scale = st.slider("", 0.5, 4.0, 1.8, step=0.1, label_visibility="collapsed")
            st.markdown("---")
            st.markdown("**🏁 Transparansi Kolom (Opasitas):**")
            col_opacity = st.slider("", 0.1, 1.0, 0.6, step=0.1, label_visibility="collapsed")

        # Color Legend HTML
        legend_html = ""
        if color_by == "Tingkat Kerawanan Banjir":
            legend_html = """
            <div class="card" style="border-color: #fca5a5;">
                <div style="font-size:0.78rem; color:#ef4444; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:12px;">⚠️ Kelas Kerawanan Banjir</div>
                <div class="band-row"><div class="band-dot" style="background:#ef4444;"></div><div class="band-name">Sangat Rawan</div><div class="band-val">""" + f"{fvi_counts.get('Sangat Rawan', 0)*px_ha:,.0f} Ha" + """</div></div>
                <div class="band-row"><div class="band-dot" style="background:#f97316;"></div><div class="band-name">Rawan</div><div class="band-val">""" + f"{fvi_counts.get('Rawan', 0)*px_ha:,.0f} Ha" + """</div></div>
                <div class="band-row"><div class="band-dot" style="background:#eab308;"></div><div class="band-name">Cukup Rawan</div><div class="band-val">""" + f"{fvi_counts.get('Cukup Rawan', 0)*px_ha:,.0f} Ha" + """</div></div>
                <div class="band-row"><div class="band-dot" style="background:#84cc16;"></div><div class="band-name">Aman</div><div class="band-val">""" + f"{fvi_counts.get('Aman', 0)*px_ha:,.0f} Ha" + """</div></div>
                <div class="band-row"><div class="band-dot" style="background:#10b981;"></div><div class="band-name">Sangat Aman</div><div class="band-val">""" + f"{fvi_counts.get('Sangat Aman', 0)*px_ha:,.0f} Ha" + """</div></div>
            </div>
            """
        elif color_by == "Tutupan Lahan":
            legend_html = '<div class="card" style="max-height: 290px; overflow-y: auto;">'
            legend_html += '<div style="font-size:0.78rem; color:#1e3a8a; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:12px;">🌿 Kategori Tutupan Lahan</div>'
            for lc_name, color in lc_palette.items():
                count = len(df[df['clean_layer'] == lc_name])
                if count > 0:
                    legend_html += f'<div class="band-row"><div class="band-dot" style="background:{color};"></div><div class="band-name" style="font-size:0.8rem;">{lc_name.title()}</div><div class="band-val" style="font-size:0.8rem;">{count*px_ha:,.0f} Ha</div></div>'
            legend_html += '</div>'
        else:
            legend_html = f"""
            <div class="card">
                <div style="font-size:0.78rem; color:#1e3a8a; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:12px;">📊 Informasi Terrain</div>
                <div style="font-size:0.85rem; color:#334155; line-height:2.2;">
                    ⛰️ <b>Elevasi Maksimal:</b> {df['elevation'].max():.1f} mdpl<br>
                    📉 <b>Elevasi Minimal:</b> {df['elevation'].min():.1f} mdpl<br>
                    📊 <b>Rerata Ketinggian:</b> {df['elevation'].mean():.1f} mdpl<br>
                    🎯 <b>Rerata Kelerengan:</b> {df['slope'].mean():.1f}°<br>
                </div>
            </div>
            """
        st.markdown(legend_html, unsafe_allow_html=True)

    with col_map:
        df_plot = df.copy()
        df_plot['elevation'] = df_plot['elevation'].round(1)
        df_plot['slope'] = df_plot['slope'].round(1)

        if color_by == "Tingkat Kerawanan Banjir":
            df_plot['color'] = df_plot['color_fvi']
        elif color_by == "Ketinggian (Elevasi)":
            el_norm = (df_plot['elevation'] - df_plot['elevation'].min()) / (df_plot['elevation'].max() - df_plot['elevation'].min() + 1)
            df_plot['color'] = el_norm.apply(lambda v: [int(6 + v*119), int(182 - v*116), int(212 - v*50), 200])
        elif color_by == "Kemiringan (Slope)":
            sl_norm = (df_plot['slope'] - df_plot['slope'].min()) / (df_plot['slope'].max() - df_plot['slope'].min() + 1)
            df_plot['color'] = sl_norm.apply(lambda v: [int(16 + v*220), int(185 - v*150), int(129 - v*100), 200])
        else:
            df_plot['color'] = df_plot['clean_layer'].apply(lambda lc: [int(lc_palette[lc].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)] + [200] if lc in lc_palette else [100, 100, 100, 150])

        layer = pdk.Layer(
            "ColumnLayer", data=df_plot,
            get_position="[lon, lat]", get_elevation="elevation",
            elevation_scale=elev_scale, radius=150,
            get_fill_color="color", pickable=True, auto_highlight=True,
            opacity=col_opacity,
        )
        view = pdk.ViewState(
            latitude=df_plot['lat'].mean(), longitude=df_plot['lon'].mean(),
            zoom=9.8, min_zoom=9.5, max_zoom=13.0, pitch=45, bearing=8
        )
        deck = pdk.Deck(
            layers=[layer], initial_view_state=view,
            map_style=pdk.map_styles.CARTO_DARK,
            views=[pdk.View(
                type="MapView",
                controller={
                    "dragPan": False,
                    "scrollZoom": {"zoomToCenter": True},
                    "doubleClickZoom": {"zoomToCenter": True},
                    "touchZoom": {"zoomToCenter": True}
                }
            )],
            tooltip={
                "html": "<div style='font-family:Inter,sans-serif;font-size:0.8rem;padding:6px;'><b>{clean_layer}</b><br>⚠️ Status: {flood_class}<br>⛰️ Elevasi: {elevation} m<br>📐 Slope: {slope}°</div>",
                "style": {"background": "#0f172a", "color": "white", "borderRadius": "8px"}
            }
        )
        st.pydeck_chart(deck, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PETA PARAMETER GEOGRAFIS (2D)
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">🗺️ Peta Parameter Geografis (2D Leaflet)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Sebaran spasial parameter utama penentu risiko banjir: tutupan lahan (vektor BIG) dan terrain morfologi</div>', unsafe_allow_html=True)

    col_lc_map, col_lc_stat = st.columns([1.6, 1])

    with col_lc_map:
        with st.container(border=True):
            # Kontrol UI untuk Peta
            col_ctrl_a, col_ctrl_b = st.columns([1.2, 1.8])
            with col_ctrl_a:
                basemap_choice = st.selectbox(
                    "Peta Dasar (Basemap):",
                    ["Terang (CartoDB)", "Jalan (OpenStreetMap)", "Satelit (Esri/World Imagery)"]
                )
            with col_ctrl_b:
                show_overlay = st.toggle("Tampilkan Lapisan Overlay", value=True)
                opacity_val = st.slider("Transparansi Lapisan:", 0.0, 1.0, 0.4, step=0.1)

            center_lat = df['lat'].mean()
            center_lon = df['lon'].mean()
            
            # Bound map view strictly
            min_lat = df['lat'].min() - 0.05
            max_lat = df['lat'].max() + 0.05
            min_lon = df['lon'].min() - 0.05
            max_lon = df['lon'].max() + 0.05
            
            # Memilih tema basemap
            if basemap_choice == "Jalan (OpenStreetMap)":
                tiles_theme = "OpenStreetMap"
            elif basemap_choice == "Satelit (Esri/World Imagery)":
                tiles_theme = None
            else:
                tiles_theme = "CartoDB positron nolabels"

            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=11,
                min_zoom=10,
                max_zoom=14,
                max_bounds=[[min_lat, min_lon], [max_lat, max_lon]],
                max_bounds_viscosity=1.0,
                scrollWheelZoom='center',
                doubleClickZoom='center',
                tiles=tiles_theme
            )

            # Jika memilih Satelit, tambahkan layer satelit Esri dan labelnya
            if basemap_choice == "Satelit (Esri/World Imagery)":
                folium.TileLayer(
                    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                    attr="Esri World Imagery",
                    name="Satelit"
                ).add_to(m)
                folium.TileLayer(
                    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
                    attr="Esri Labels",
                    name="Labels",
                    overlay=True,
                    control=False
                ).add_to(m)

            if show_overlay and gdf is not None:
                def style_lc(feature):
                    lc = feature['properties'].get('clean_layer', '')
                    return {
                        'fillColor': lc_palette.get(lc, '#94a3b8'),
                        'color': 'white', 'weight': 0.5, 'fillOpacity': opacity_val
                    }
                folium.GeoJson(
                    gdf, style_function=style_lc,
                    tooltip=folium.GeoJsonTooltip(fields=['clean_layer'], aliases=['Tutupan Lahan:'])
                ).add_to(m)

            # Jika menggunakan CartoDB, taruh label jalan di atas overlay
            if basemap_choice == "Terang (CartoDB)":
                folium.TileLayer(
                    tiles="CartoDB positron onlylabels",
                    name="Label Jalan & Lokasi",
                    overlay=True,
                    control=False
                ).add_to(m)



            st_folium(m, use_container_width=True, height=450, returned_objects=[])

    with col_lc_stat:
        lc_counts = df['clean_layer'].value_counts().reset_index()
        lc_counts.columns = ['Tutupan', 'Jumlah']
        lc_counts['Ha'] = lc_counts['Jumlah'] * px_ha
        lc_counts['Pct'] = (lc_counts['Jumlah'] / total * 100).round(1)
        lc_counts['warna'] = lc_counts['Tutupan'].map(lc_palette).fillna('#94a3b8')

        lc_html = '<div class="card"><b>Komposisi Tutupan Lahan</b><div style="margin-top:10px;">'
        for _, row in lc_counts.iterrows():
            lc_html += f"""
            <div class="band-row">
                <div class="band-dot" style="background:{row['warna']};"></div>
                <div class="band-name" style="font-size:0.82rem;">{row['Tutupan'].title()}</div>
                <div class="band-val" style="font-size:0.85rem;">{row['Ha']:,.0f} Ha</div>
                <div class="band-pct">{row['Pct']}%</div>
            </div>"""
        lc_html += '</div></div>'
        st.markdown(lc_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — STATISTIK & HUBUNGAN SPASIAL
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">📊 Profil Statistik & Analisis Spasial Kerawanan</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Analisis distribusi kelas kerawanan banjir dan keterkaitannya dengan penggunaan lahan</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 1.2])

    with col_a:
        with st.container(border=True):
            st.markdown("**Distribusi Zona Kerawanan Banjir (Hektar)**")
            risk_df = pd.DataFrame({
                'Risk Class': ['Sangat Aman', 'Aman', 'Cukup Rawan', 'Rawan', 'Sangat Rawan'],
                'Ha': [
                    fvi_counts.get('Sangat Aman', 0) * px_ha,
                    fvi_counts.get('Aman', 0) * px_ha,
                    fvi_counts.get('Cukup Rawan', 0) * px_ha,
                    fvi_counts.get('Rawan', 0) * px_ha,
                    fvi_counts.get('Sangat Rawan', 0) * px_ha
                ],
                'Color': ['#10b981', '#84cc16', '#eab308', '#f97316', '#ef4444']
            })
            chart_risk = alt.Chart(risk_df).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
                x=alt.X('Risk Class:N', sort=['Sangat Aman', 'Aman', 'Cukup Rawan', 'Rawan', 'Sangat Rawan'], title="Kelas Kerawanan"),
                y=alt.Y('Ha:Q', title="Luas Area (Hektar)"),
                color=alt.Color('Risk Class:N', scale=alt.Scale(
                    domain=['Sangat Aman', 'Aman', 'Cukup Rawan', 'Rawan', 'Sangat Rawan'],
                    range=['#10b981', '#84cc16', '#eab308', '#f97316', '#ef4444']
                ), legend=None),
                tooltip=['Risk Class', 'Ha']
            ).properties(height=300)
            st.altair_chart(chart_risk, use_container_width=True)

    with col_b:
        with st.container(border=True):
            st.markdown("**Proporsi Tingkat Kerawanan Berdasarkan Tutupan Lahan**")
            # Cross-tabulation of land cover and risk class
            cross_tab = pd.crosstab(df['clean_layer'], df['flood_class']).reset_index()
            cross_melt = cross_tab.melt(id_vars='clean_layer', var_name='Risk Class', value_name='Count')
            cross_melt['Ha'] = cross_melt['Count'] * px_ha
            
            chart_cross = alt.Chart(cross_melt).mark_bar().encode(
                x=alt.X('sum(Ha):Q', stack="normalize", title="Proporsi Luas (%)", axis=alt.Axis(format='%')),
                y=alt.Y('clean_layer:N', sort='-x', title="Tutupan Lahan"),
                color=alt.Color('Risk Class:N', scale=alt.Scale(
                    domain=['Sangat Aman', 'Aman', 'Cukup Rawan', 'Rawan', 'Sangat Rawan'],
                    range=['#10b981', '#84cc16', '#eab308', '#f97316', '#ef4444']
                ), title="Tingkat Kerawanan"),
                tooltip=['clean_layer', 'Risk Class', 'Ha']
            ).properties(height=300)
            st.altair_chart(chart_cross, use_container_width=True)

    # Secondary statistics
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        with st.container(border=True):
            st.markdown("🏔️ **Karakteristik Elevasi**")
            st.write(f"Rerata ketinggian wilayah Kota Sorong adalah **{df['elevation'].mean():.1f} mdpl**. Zona rawan banjir terakumulasi secara dominan pada dataran rendah di bawah ketinggian **10 mdpl**.")

    with col_c2:
        with st.container(border=True):
            st.markdown("📐 **Distribusi Kelerengan**")
            st.write(f"Sebagian besar wilayah memiliki kemiringan landai. Rerata slope adalah **{df['slope'].mean():.1f}°**. Area dengan slope **< 2°** memiliki akumulasi bahaya banjir tertinggi.")

    with col_c3:
        with st.container(border=True):
            st.markdown("🏘️ **Kritis Permukiman**")
            st.write(f"Dari total **{permukiman_total * px_ha:,.0f} Ha** permukiman di Sorong, sebesar **{pct_permukiman_rawan:.1f}% ({area_permukiman_rawan:,.0f} Ha)** berada di zona Rawan & Sangat Rawan.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ANALISIS & MITIGASI BENCANA
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">💡 Temuan Analisis & Rekomendasi Mitigasi</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Wawasan geospasial kuantitatif serta saran akademis untuk penanggulangan bencana banjir di Kota Sorong</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="insight-box-warn">
        🌊 <strong>Faktor Utama Kerawanan (Geomorfologi & Antropogenik)</strong><br>
        Sebesar <strong>{pct_rawan_sangat_rawan:.1f}% ({area_rawan_sangat_rawan:,.0f} Ha)</strong> dari wilayah Kota Sorong masuk dalam kategori <strong>Rawan</strong> dan <strong>Sangat Rawan</strong> banjir. 
        Kombinasi elevasi rendah (< 10 meter mdpl) di area pesisir, lereng yang datar (< 1°-2°), dan alih fungsi lahan menjadi <strong>Permukiman</strong> (yang menyumbang koefisien limpasan air permukaan / runoff tertinggi) menjadi penyebab utama genangan banjir berulang di perkotaan Sorong.
    </div>
    <div class="insight-box">
        🚨 <strong>Kritis Wilayah Terbangun (Permukiman)</strong><br>
        Analisis overlay spasial menunjukkan bahwa <strong>{pct_permukiman_rawan:.1f}% ({area_permukiman_rawan:,.0f} Ha)</strong> kawasan permukiman di Kota Sorong berada langsung di dalam zona berisiko tinggi. Kurangnya koefisien drainase permukaan akibat perkerasan tanah meningkatkan kecepatan akumulasi debit banjir saat intensitas hujan tinggi.
    </div>
    <div class="insight-box-suggest">
        🛠️ <strong>Rekomendasi Mitigasi Struktural (Teknis Basah & Hijau)</strong><br>
        1. <strong>Pembangunan Kolam Retensi (Retention Ponds):</strong> Di area aliran sungai utama perkotaan untuk menampung puncak debit limpasan sebelum masuk ke saluran mikro kota.<br>
        2. <strong>Normalisasi & Pengerukan Drainase:</strong> Pembersihan sedimentasi pada saluran pembuangan utama guna meningkatkan kapasitas hidrolik saluran air.<br>
        3. <strong>Penerapan SuDS (Sustainable Drainage Systems):</strong> Menggunakan paving berpori (permeable pavement), bioretensi (bioswales), dan sumur resapan komunal di area perumahan padat.<br>
        4. <strong>Restorasi Sabuk Hijau Mangrove:</strong> Melindungi wilayah pesisir Sorong dari potensi banjir pasang air laut (rob) yang memperparah banjir luapan sungai.
    </div>
    <div class="insight-box-suggest">
        📋 <strong>Rekomendasi Non-Struktural (Perencanaan & Kebijakan)</strong><br>
        1. <strong>Pengendalian RTRW (Rencana Tata Ruang Wilayah):</strong> Pembatasan izin pembangunan baru di zona klasifikasi "Sangat Rawan" banjir.<br>
        2. <strong>Pembuatan Peta Evakuasi Dini:</strong> Menggunakan peta kerawanan ini sebagai dasar perencanaan jalur evakuasi aman berbasis komunitas di tingkat kelurahan.<br>
        3. <strong>Reboisasi DAS Hulu:</strong> Penghijauan kembali kawasan perbukitan terjal di hulu tangkapan air Sorong untuk meminimalkan debit limpasan ke dataran rendah.
    </div>
    """, unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <div>
        <h4>Sistem Pemetaan Kerawanan Banjir Kota Sorong</h4>
        <p>Aplikasi Pendukung Keputusan Mitigasi Bencana Banjir Berbasis GIS &amp; Multi-Criteria Evaluation (MCE)<br>Sumber Data: DEM SRTM (USGS) &amp; Peta Rencana Tata Ruang/Tutupan Lahan BIG</p>
    </div>
    <div>
        <span class="footer-badge">Aplikasi GIS Interaktif</span>
        <div class="footer-names">Kelompok 10 · Kolaborasi QGIS &amp; Streamlit Python</div>
    </div>
</div>
""", unsafe_allow_html=True)
