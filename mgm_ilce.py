import requests
import warnings
import pandas as pd
import plotly.figure_factory as ff
import numpy as np

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

class MGMWeather:
    def __init__(self, location):
        self.location = self.clear_tr_character(location)
        self.location_id = None
        self.latitude = None
        self.longitude = None
        self.current_degree = None
        self.district_name = None
        self.target_location_details = None

    def clear_tr_character(self, city_name):
        replacements = {
            "ı": "i", "ü": "u", "ğ": "g", "ş": "s", "ö": "o", "ç": "c"
        }
        for tr_char, lat_char in replacements.items():
            city_name = city_name.replace(tr_char, lat_char)
        return city_name.lower()

    def request(self, url):
        headers = {
            "Host": "servis.mgm.gov.tr",
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
            "Origin": "https://www.mgm.gov.tr"
        }
        response = requests.get(url, headers=headers, verify=False)
        return response.json()

    def fetch_data(self):
        city_data_url = f"https://servis.mgm.gov.tr/web/merkezler?il={self.location}"
        city_data = self.request(city_data_url)

        if not isinstance(city_data, list) or len(city_data) == 0:
            print(f"No data found for {self.location}")
            return
        
        self.location_id = city_data[0].get("merkezId")
        self.longitude = city_data[0].get("boylam")
        self.latitude = city_data[0].get("enlem")

        city_current_weather_url = f"https://servis.mgm.gov.tr/web/sondurumlar?merkezid={self.location_id}"
        city_current_weather = self.request(city_current_weather_url)

        if not isinstance(city_current_weather, list) or len(city_current_weather) == 0:
            print(f"No weather data found for {self.location}")
            return
        
        self.current_degree = city_current_weather[0].get("sicaklik")

    def get_current_temperature(self):
        self.fetch_data()
        return self.current_degree

    def district(self, d=None):
        if d:
            self.district_name = self.clear_tr_character(d)
            self.get_district_data()
        return self.target_location_details.get('ilce', '') if self.target_location_details else ''
    
    def get_district_data(self):
        if not self.district_name:
            print("No district name provided.")
            return
        
        district_data_url = f"https://servis.mgm.gov.tr/web/merkezler?il={self.location}&ilce={self.district_name}"
        district_data = self.request(district_data_url)

        if not isinstance(district_data, list) or len(district_data) == 0:
            print(f"No district data found for {self.district_name} in {self.location}")
            return

        self.target_location_details = district_data[0]
        self.location_id = self.target_location_details.get("merkezId")
        self.longitude = self.target_location_details.get("boylam")
        self.latitude = self.target_location_details.get("enlem")
        self.fetch_district_weather_data()

    def fetch_district_weather_data(self):
        if not self.location_id:
            print("No location ID found.")
            return
        
        district_weather_url = f"https://servis.mgm.gov.tr/web/sondurumlar?merkezid={self.location_id}"
        district_weather = self.request(district_weather_url)

        if not isinstance(district_weather, list) or len(district_weather) == 0:
            print(f"No weather data found for district {self.district_name} in {self.location}")
            return
        
        self.current_degree = district_weather[0].get("sicaklik")
        print(f"Current Temperature in {self.location} - {self.district_name}: {self.current_degree} °C")

def get_all_provinces():
    return {
        "adana": ["merkez", "seyhan", "cukurova", "yuregir", "ceyhan", "sarıçam", "akdeniz", "karaisalı", "karataş"],
        # Diğer iller ve ilçeler
    }

def fetch_all_weather_data():
    provinces = get_all_provinces()
    weather_data = []

    for province, districts in provinces.items():
        weather = MGMWeather(province)
        for district in districts:
            weather.district(district)
            if weather.current_degree is not None:
                weather_data.append({
                    "Province": province.title(),
                    "District": district.title(),
                    "Latitude": weather.latitude,
                    "Longitude": weather.longitude,
                    "Temperature": weather.current_degree
                })

    df = pd.DataFrame(weather_data)
    return df

def plot_temperature_on_map(df):
    df_filtered = df[df['Temperature'] != -9999]

    fig = ff.create_hexbin_mapbox(
        data_frame=df_filtered, 
        lat="Latitude", 
        lon="Longitude", 
        color="Temperature", 
        nx_hexagon=5,  # Altıgen boyutlarını büyütmek için daha küçük bir değer
        opacity=0.6,
        labels={"Temperature": "Temperature (°C)"},
        color_continuous_scale="YlOrRd",
        show_original_data=True
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=5,
        mapbox_center={"lat": np.mean(df_filtered['Latitude']), "lon": np.mean(df_filtered['Longitude'])},
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    fig.write_html("map.html")
    print("map.html dosyası oluşturuldu.")

if __name__ == "__main__":
    df_weather = fetch_all_weather_data()
    plot_temperature_on_map(df_weather)
