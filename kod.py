import pandas as pd
from geopy.geocoders import Nominatim
import plotly.express as px
import time

# Geocoder'ı başlat
geolocator = Nominatim(user_agent="geoapiExercises")

# CSV dosyasını oku
df = pd.read_csv("ports_and_details.csv")

# Enlem ve boylam sütunlarını ekle
df["latitude"] = None
df["longitude"] = None

# Enlem ve boylamı almak için fonksiyon
def get_lat_lon(sehir, ilce):
    location = geolocator.geocode(f"{ilce}, {sehir}, Türkiye")
    if location:
        return location.latitude, location.longitude
    return None, None

# Tüm satırlar için enlem ve boylam bilgilerini doldur
for index, row in df.iterrows():
    sehir = row["Şehir"]
    ilce = row["İlçe"]
    lat, lon = get_lat_lon(sehir, ilce)
    df.at[index, "latitude"] = lat
    df.at[index, "longitude"] = lon
    time.sleep(1)  # API taleplerini yavaşlatmak için

# Boş enlem-boylam verilerini çıkar
df = df.dropna(subset=["latitude", "longitude"])

# Altıgen haritayı oluştur
fig = px.density_mapbox(
    df,
    lat="latitude",
    lon="longitude",
    z="Sıcaklık",  # Sıcaklık verisi için
    radius=10,  # Altıgen boyutu
    center=dict(lat=38.9637, lon=35.2433),  # Türkiye'nin merkezi
    zoom=5,
    mapbox_style="carto-positron",
    title="Türkiye Sıcaklık Dağılımı - Altıgen Görselleştirme"
)

fig.update_layout(
    mapbox=dict(
        center=dict(lat=38.9637, lon=35.2433),
        zoom=5
    ),
    title="Türkiye'deki Sıcaklık Dağılımı (Hexbin)"
)

fig.show()
