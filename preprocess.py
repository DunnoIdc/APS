import os
import numpy as np
import pandas as pd
import geopandas as gpd
from PIL import Image
from pyproj import Transformer
from shapely.geometry import Point

def preprocess_gis_data():
    print("--- 1. Memproses Data Raster (DEM & Slope) ---")
    
    # Membuka file raster
    img_dem = Image.open("Dem_meter_fix.tif")
    arr_dem = np.array(img_dem)
    
    img_slope = Image.open("Slope paling baru.tif")
    arr_slope = np.array(img_slope)
    
    # Ambil metadata spatial reference (tiepoint & pixel scale)
    tiepoint = img_dem.tag.get(33922)
    scale = img_dem.tag.get(33550)
    
    x0, y0 = tiepoint[3], tiepoint[4]
    dx, dy = scale[0], scale[1]
    
    # EPSG:32752 (UTM zone 52S) ke EPSG:4326 (Lat/Lon)
    transformer = Transformer.from_crs("epsg:32752", "epsg:4326", always_xy=True)
    
    # Downsample factor (25 berarti mengambil setiap 25 pixel untuk performa web)
    downsample = 25
    rows, cols = arr_dem.shape
    
    row_indices = np.arange(0, rows, downsample)
    col_indices = np.arange(0, cols, downsample)
    
    raster_points = []
    for r in row_indices:
        for c in col_indices:
            val_dem = arr_dem[r, c]
            val_slope = arr_slope[r, c]
            
            # Abaikan data kosong (NoData)
            if np.isnan(val_dem) or np.isnan(val_slope) or val_slope == -9999.0 or val_dem < -500:
                continue
                
            # Hitung koordinat UTM
            utm_x = x0 + c * dx + dx / 2.0
            utm_y = y0 - r * dy - dy / 2.0
            
            # Ubah ke Lat/Lon
            lon, lat = transformer.transform(utm_x, utm_y)
            raster_points.append({
                'lat': lat,
                'lon': lon,
                'elevation': float(val_dem),
                'slope': float(val_slope)
            })
            
    df_raster = pd.DataFrame(raster_points)
    print(f"Berhasil memproses {len(df_raster)} titik grid raster.")
    
    print("\n--- 2. Memproses Data Vektor (Shapefile Tutupan Lahan) ---")
    gdf_shp = gpd.read_file("Tutupan_gabungan.shp")
    
    # Fungsi pembersihan nama kategori tutupan lahan
    def clean_lc_name(name):
        if not name:
            return "Lahan Terbuka"
        # Hilangkan prefix peta RBI
        cleaned = name.replace("RBI25K_KOTA SORONG_KUGI50 — ", "").replace("_AR_25K", "")
        cleaned = cleaned.replace("RBI25K_KOTA SORONG_KUGI50 \x97 ", "")
        # Rapikan spasi nama
        cleaned = cleaned.replace("HERBADANRUMPUT", "HERBA DAN RUMPUT")
        cleaned = cleaned.replace("HUTANLAHANRENDAH", "HUTAN LAHAN RENDAH")
        cleaned = cleaned.replace("HUTANLAHANTINGGI", "HUTAN LAHAN TINGGI")
        cleaned = cleaned.replace("HUTANMANGROVE", "HUTAN MANGROVE")
        cleaned = cleaned.replace("PENUTUP_LAHAN", "PENUTUP LAHAN")
        cleaned = cleaned.replace("SEMAKBELUKAR", "SEMAK BELUKAR")
        cleaned = cleaned.replace("TANAMANCAMPUR", "TANAMAN CAMPUR")
        return cleaned
        
    gdf_shp['clean_layer'] = gdf_shp['layer'].apply(clean_lc_name)
    
    # Sederhanakan geometri untuk mempercepat spasial join (toleransi ~55 meter)
    gdf_shp['geometry'] = gdf_shp['geometry'].simplify(tolerance=0.0005, preserve_topology=True)
    gdf_shp_light = gdf_shp[['clean_layer', 'geometry']]
    
    # Simpan versi GeoJSON ringan untuk peta leaflet
    gdf_shp_light.to_file("tutupan_lahan.geojson", driver="GeoJSON")
    print("Berhasil menyimpan tutupan_lahan.geojson")
    
    print("\n--- 3. Menggabungkan Data (Spatial Join) ---")
    # Konversi titik raster ke GeoDataFrame
    geometry = [Point(xy) for xy in zip(df_raster['lon'], df_raster['lat'])]
    gdf_grid = gpd.GeoDataFrame(df_raster, geometry=geometry, crs="EPSG:4326")
    
    # Spatial join
    gdf_joined = gpd.sjoin(gdf_grid, gdf_shp_light, how="left", predicate="within")
    
    # Resolusi area yang tumpang tindih (prioritaskan kategori spesifik dibanding "PENUTUP LAHAN")
    def resolve_overlap(group):
        if len(group) == 1:
            return group.iloc[0]
        valid = group[group['clean_layer'].notna()]
        if len(valid) == 0:
            return group.iloc[0]
        specific = valid[valid['clean_layer'] != "PENUTUP LAHAN"]
        if len(specific) > 0:
            return specific.iloc[0]
        return valid.iloc[0]
        
    gdf_cleaned = gdf_joined.groupby(['lat', 'lon'], as_index=False).apply(resolve_overlap)
    
    # Simpan hasil akhir ke CSV terkompresi
    df_final = gdf_cleaned.drop(columns=['geometry', 'index_right'])
    df_final['clean_layer'] = df_final['clean_layer'].fillna("PENUTUP LAHAN")
    
    output_csv = "data_spasial.csv.gz"
    df_final.to_csv(output_csv, index=False, compression="gzip")
    print(f"Berhasil menyimpan database terintegrasi: {output_csv} ({len(df_final)} titik)")

if __name__ == "__main__":
    preprocess_gis_data()
