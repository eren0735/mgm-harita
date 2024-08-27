import requests
import pandas as pd
import folium
import sys

# Konsol çıktısını UTF-8 olarak ayarlıyoruz
sys.stdout.reconfigure(encoding='utf-8')

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
        response = requests.get(url, headers=headers)
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
        
        # İlçeye özel veri almak için doğru URL'yi kullanıyoruz
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
        "adıyaman": ["merkez", "kahta", "besni", "gerger", "gölbaşı", "samsat", "çelikhan", "doluca", "tut"],
        "afyonkarahisar": ["merkez", "sandıklı", "çobanlar", "dazkırı", "dinar", "kızılören", "sinanpaşa", "sultandağı", "yaylalar", "eğirdir", "bolvadin"],
        "ağrı": ["merkez", "doğubayazıt", "patnos", "hamur", "eleşkirt", "tutak", "yüksekova", "çaldıran", "gülağaç"],
        "aksaray": ["merkez", "ağaçören", "eskil", "güzelyurt", "sarıyahşi", "ortaköy", "kızılkaya", "özkonak", "dinek", "sarıyakup"],
        "amasya": ["merkez", "göynücek", "gümüşhacıköy", "merzifon", "suluova", "taşova", "hamamözü", "biladık", "yassıören"],
        "ankara": ["cankaya", "kecioren", "mamak", "yenimahalle", "besevler", "altındağ", "etimesgut", "sincan", "gölbaşı", "polatlı"],
        "antalya": ["merkez", "alanya", "döşemealtı", "konyaaltı", "kepez", "kemer", "manavgat", "serik", "gazipaşa", "akseki"],
        "artvin": ["merkez", "ardanuç", "şavşat", "borçka", "yusufeli", "hopa", "murgul", "savsat", "yaylalar", "ardanuç"],
        "aydin": ["merkez", "efeler", "söke", "kuyucak", "bozdoğan", "karacasu", "nazilli", "ydıdım", "çine", "köşk"],
        "balıkesir": ["merkez", "altıeylül", "karesi", "bandırma", "burhaniye", "edremit", "ayvalık", "sındırgı", "gönen", "bigadiç"],
        "bartın": ["merkez", "ağdacı", "ulucami", "kurucaşile", "şirinler", "balat", "gölbucağı", "abdipaşa", "müftü", "beyazıt"],
        "bayburt": ["merkez", "aşkale", "hasanbeyli", "yıldızkent", "gökçedere", "köyceğiz", "otlak", "ağıllı"],
        "bilecik": ["merkez", "bozüyük", "pazaryeri", "yenipazar", "söğüt", "vezirhan", "osmaneli", "bilecik", "söğüt"],
        "bingöl": ["merkez", "kiğı", "solhan", "yedisu", "genç", "yayladere", "karlıova", "adaklı"],
        "bitlis": ["merkez", "adilcevaz", "tatvan", "hizan", "güroymak", "ahlat", "mutki", "bitlis"],
        "bolu": ["merkez", "gerede", "dörtdivan", "kıbrıs", "yeniçağa", "mudurnu", "seben", "köroğlu"],
        "burdur": ["merkez", "bucak", "gölhisar", "karamanlı", "yeşilova", "tefenni", "çavdır", "burdur"],
        "bursa": ["merkez", "nilüfer", "osmangazi", "yıldırım", "görükle", "orhangazi", "mudanya", "karacabey", "gemlik"],
        "çanakkale": ["merkez", "biga", "gelibolu", "lapseki", "eymen", "bozcaada", "yazılı", "çan", "dardanos"],
        "çankırı": ["merkez", "atkaracalar", "kurşunlu", "orta", "ilgaz", "şabanözü", "kızılırmak", "çerkeş"],
        "çorum": ["merkez", "osmanbey", "sungurlu", "mecitözü", "laçin", "boğazkale", "ortaköy", "yıldız", "ula"],
        "denizli": ["merkez", "merkezefendi", "acıpayam", "beyağaç", "serinhisar", "tavas", "buldan", "honaz", "çivril"],
        "diyarbakır": ["merkez", "bismil", "çınar", "silvan", "ergani", "kayapınar", "hani", "sur", "lice"],
        "düzce": ["merkez", "akçakoca", "kaynaşlı", "gölyaka", "cumayeri", "duzce"],
        "edirne": ["merkez", "keşan", "uzunköprü", "saray", "ipek"],
        "elazığ": ["merkez", "karakoçan", "maden", "sivrice", "palu", "keban", "haran", "aricak"],
        "erzincan": ["merkez", "üzümlü", "sivas", "kemaliye", "tunceli", "yusufeli", "ilıca"],
        "erzurum": ["merkez", "palandöken", "yakutiye", "aziziye", "narman", "horasan", "tuzluca"],
        "eskişehir": ["merkez", "tepebaşı", "odunpazarı", "sarıcakaya", "beylikova", "söğüt", "mihalıççık"],
        "gaziantep": ["merkez", "şahinbey", "şehitkamil", "şehitkadir", "nizip", "karkamış", "oğuzeli", "araban", "kobani"],
        "giresun": ["merkez", "espiye", "görele", "tirebolu", "bulancak", "alucra", "yağlıdere"],
        "gümüşhane": ["merkez", "köse", "şiran", "torul", "kürtün"],
        "hakkari": ["merkez", "şemdinli", "yüksekova", "çukurca", "hakkari"],
        "hatay": ["merkez", "antakya", "defne", "dörtyol", "iskenderun", "yayladağı", "reşatbey"],
        "ısparta": ["merkez", "eğirdir", "gölcük", "senirkent", "şarkikaraağaç", "keçiborlu"],
        "istanbul": ["kadıköy", "üsküdar", "beşiktaş", "fatih", "beyoğlu", "bakırköy", "avcılar", "bahçelievler", "esenyurt", "silivri"],
        "izmir": ["merkez", "konak", "karşıyaka", "gaziemir", "buca", "bornova", "torbalı", "çeşme", "urla"],
        "kahramanmaraş": ["merkez", "dulkadiroğlu", "onikişubat", "elbistan", "afşin", "pazarcık", "eğin", "göksun"],
        "karabük": ["merkez", "safranbolu", "yenice", "barta", "karabük"],
        "karaman": ["merkez", "ergün", "kazımkarabekir", "karaman"],
        "kars": ["merkez", "arpaçay", "selim", "digor", "kağızman", "sarıkamış"],
        "kastamonu": ["merkez", "tosya", "daday", "pınarbaşı", "ayancık", "km"],
        "kayseri": ["merkez", "melikgazi", "kocasinan", "talas", "hacılar", "develi", "bünyan", "sarkışla", "özvatan"],
        "kırıkkale": ["merkez", "keskin", "delice", "karakeçili", "yahşihan", "balışeyh", "suluova"],
        "kırklareli": ["merkez", "lüleburgaz", "pınarhisar", "vize", "babaeski", "kofçaz", "pehlivanköy"],
        "kırşehir": ["merkez", "mucur", "kaman", "akpınar", "çiçekdağı", "boztepe"],
        "konya": ["merkez", "selçuklu", "karatay", "meram", "akşehir", "ereğli", "hüyük", "cihanbeyli", "sarayönü"],
        "kocaeli": ["merkez", "izmit", "gebze", "kartepe", "derince", "çayırova", "darıca", "körfez"],
        "kütahya": ["merkez", "simav", "tavşanlı", "emet", "domaniç", "gediz", "aslanapa"],
        "malatya": ["merkez", "akçadağ", "battalgazi", "hekimhan", "pütürge", "yarıklı", "kuluncak"],
        "manisa": ["merkez", "salihli", "gördes", "turgutlu", "saruhanlı", "köprübaşı", "soma", "demirtaş"],
        "marş": ["merkez", "nizip", "şahinbey", "şehitkamil", "şehitkadir", "karkamış", "birecik"],
        "mardin": ["merkez", "midyat", "nusaybin", "derik", "dargeçit", "mazıdağı", "artuklu", "savur"],
        "muğla": ["merkez", "bodrum", "marmaris", "datça", "yataklı", "milas", "ortaca"],
        "muş": ["merkez", "bulanık", "malazgirt", "varto", "korkut", "hasköy"],
        "nevşehir": ["merkez", "avanos", "derinkuyu", "gülşehir", "kızılkaya", "hacıbektaş"],
        "niğde": ["merkez", "altunhisar", "bor", "çamardı", "üçkuyu", "sazlıpınar"],
        "ordu": ["merkez", "ünye", "gölköy", "fatsa", "niksar", "korgan", "kabadüz", "gölkaya"],
        "osmaniye": ["merkez", "düziçi", "toprakkale", "hasanbeyli", "sumbas", "bahçe"],
        "rize": ["merkez", "ayder", "çamlıhemşin", "ardanuç", "çayeli", "pazar"],
        "sakarya": ["merkez", "adapazarı", "serdivan", "sapanca", "karasu", "akyazı", "hendek"],
        "samsun": ["merkez", "atalay", "tekkeköy", "vezirköprü", "bafra", "havza", "19 Mayıs"],
        "siirt": ["merkez", "tillo", "kurtalan", "pervari", "baykan", "eruh"],
        "sinop": ["merkez", "boyabat", "erenkaya", "durağan", "saraydüzü", "ayancık"],
        "sivas": ["merkez", "kangal", "divriği", "gölova", "suşehri", "yıldızeli"],
        "tekirdağ": ["merkez", "süleymanpaşa", "çorlu", "malkara", "hayrabolu", "çerkezköy"],
        "tokat": ["merkez", "erzincan", "zile", "reşadiye", "niksar", "turhal"],
        "trabzon": ["merkez", "akçaabat", "yomra", "sürmene", "of", "maçka"],
        "tunceli": ["merkez", "nazimiye", "pülümür", "hazarşah", "özgüven"],
        "uşak": ["merkez", "banaz", "sivaslı", "eğri", "karahallı"],
        "van": ["merkez", "edremit", "gevaş", "çatak", "bahçesaray", "muradiye"],
        "yalova": ["merkez", "çınarcık", "armutlu", "altınova", "termal"],
        "yozgat": ["merkez", "sorgun", "yerköy", "çayıralan", "akdağmadeni", "saraykent"],
        "zonguldak": ["merkez", "karadenizereğli", "alaplı", "devrek", "ereğli", "çaycuma"],
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
    # Sıcaklık değeri -9999 olan verileri filtreleyin
    df_filtered = df[df['Temperature'] != -9999]

    # Haritayı oluşturun
    m = folium.Map(location=[39.9334, 32.8597], zoom_start=6)

    # Renk fonksiyonu
    def temperature_color(temp):
        if temp < 0:
            return 'blue'
        elif 0 <= temp < 10:
            return 'lightblue'
        elif 10 <= temp < 20:
            # Cyan rengi daha koyu tonlarla daha doğru bir şekilde ayarlıyoruz
            return folium.colors.linear.Cividis_09[temp / 20]
        elif 20 <= temp < 30:
            # Sarı rengi 20°C'den 30°C'ye doğru daha koyu tonlar kullanarak ayarlıyoruz
            return folium.colors.linear.YlOrRd_09[temp / 30]
        else:
            # Kırmızı rengi 30°C'den yüksek sıcaklıklar için kullanıyoruz
            return folium.colors.linear.RdYlBu_09[temp / 40]

    # Verileri harita üzerine ekleyin
    for idx, row in df_filtered.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=10,
            color=temperature_color(row['Temperature']),
            fill=True,
            fill_color=temperature_color(row['Temperature']),
            fill_opacity=0.6,
            popup=f"{row['District']}: {row['Temperature']}°C"
        ).add_to(m)

    # Haritayı HTML dosyası olarak kaydedin
    m.save('map.html')

# Ana kod bloğu
if __name__ == "__main__":
    df_weather = fetch_all_weather_data()
    plot_temperature_on_map(df_weather)
