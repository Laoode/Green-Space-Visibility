import folium  
from folium import plugins
import matplotlib.colors as mcolors  
import matplotlib.cm as cm  
import pandas as pd  
import geopandas as gpd  
from shapely.geometry import Point  

def create_gvi_geopackage(csv_path, output_path):  
    # Read CSV data  
    df = pd.read_csv(csv_path)  
      
    # Create geometry points  
    geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]  
      
    # Create GeoDataFrame  
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=4326)  
      
    # Save as GeoPackage  
    gdf.to_file(output_path, driver="GPKG", layer="gvi-points")  
      
    return gdf

def create_gvi_map(gdf, center_lat=-3.9778, center_lon=122.5194):  
    # Create base map centered on Kendari  
    m = folium.Map(  
        location=[center_lat, center_lon],  
        zoom_start=15,  
        tiles='OpenStreetMap'  
    )  
      
    # Normalize GVI values for color mapping  
    norm = mcolors.Normalize(vmin=gdf['gvi_average'].min(),   
                           vmax=gdf['gvi_average'].max())  
    colormap = cm.get_cmap('Greens')  
      
    # Add points to map  
    for idx, row in gdf.iterrows():  
        # Get color based on GVI value  
        color = mcolors.to_hex(colormap(norm(row['gvi_average'])))  
          
        # Create popup text  
        popup_text = f"""  
        <b>Lokasi:</b> {row['location']}<br>  
        <b>GVI Rata-rata:</b> {row['gvi_average']:.4f}<br>  
        <b>GVI Depan:</b> {row['gvi_depan']:.4f}<br>  
        <b>GVI Kiri:</b> {row['gvi_kiri']:.4f}<br>  
        <b>GVI Kanan:</b> {row['gvi_kanan']:.4f}  
        """  
          
        # Add circle marker  
        folium.CircleMarker(  
            location=[row['latitude'], row['longitude']],  
            radius=8,  
            popup=folium.Popup(popup_text, max_width=300),  
            color='black',  
            weight=1,  
            fillColor=color,  
            fillOpacity=0.8  
        ).add_to(m)  
      
    # Add color legend  
    colorbar = plugins.FloatImage(  
        create_colorbar(gdf['gvi_average'].min(), gdf['gvi_average'].max()),  
        bottom=10,  
        left=10  
    )  
    colorbar.add_to(m)  
      
    return m  
  
def create_colorbar(vmin, vmax):  
    """Create colorbar for the map"""  
    import matplotlib.pyplot as plt  
    import io  
    import base64  
      
    fig, ax = plt.subplots(figsize=(1, 4))  
    fig.subplots_adjust(right=0.5)  
      
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)  
    cb = plt.colorbar(cm.ScalarMappable(norm=norm, cmap='Greens'),   
                     cax=ax, orientation='vertical')  
    cb.set_label('Green View Index (GVI)', rotation=270, labelpad=15)  
      
    # Convert to base64 for embedding  
    img = io.BytesIO()  
    plt.savefig(img, format='png', bbox_inches='tight', dpi=100)  
    img.seek(0)  
    plot_url = base64.b64encode(img.getvalue()).decode()  
    plt.close()  
      
    return f"data:image/png;base64,{plot_url}"

def main():  
    # Load your CSV data  
    csv_path = "gvi/kendari_gvi_results.csv"  
      
    # Create GeoPackage  
    gdf = create_gvi_geopackage(csv_path, "gvi/kendari_gvi.gpkg")  
      
    # Create interactive map  
    gvi_map = create_gvi_map(gdf)  
      
    # Save map  
    gvi_map.save("maps/kendari_gvi_map.html")  
      
    # Display statistics  
    print("=== STATISTIK GVI TAMAN KOTA KENDARI ===")  
    print(f"Total titik: {len(gdf)}")  
    print(f"GVI rata-rata: {gdf['gvi_average'].mean():.4f}")  
    print(f"GVI minimum: {gdf['gvi_average'].min():.4f}")  
    print(f"GVI maksimum: {gdf['gvi_average'].max():.4f}")  
    print(f"Standar deviasi: {gdf['gvi_average'].std():.4f}")  
  
if __name__ == "__main__":  
    main()