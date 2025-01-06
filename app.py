from flask import Flask, render_template, redirect, request
import requests
import os
import ssl

app = Flask(__name__)

# WeatherAPI.com API Key
API_KEY = '51d6b1325ac14eb680543912241310'

GEOLOCATION_API = 'http://ip-api.com/json/'

app.static_folder = 'static'

# Function to get weather data by city name
def get_weather(city):
    url = f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days=10&aqi=yes&alerts=yes'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Mapping of condition codes to animation filenames
        animation_mapping = {
            "1000": "sunny.json",  # Clear sky
            "1003": "partly-cloud.json",  # Few clouds
            "1006": "cloudy.json",  # Scattered clouds
            "1009": "cloudy.json",  # Overcast clouds
            "1030": "fog.json",  # Mist
            "1063": "drizzle.json",  # Patchy rain possible
            "1183": "rain.json",  # Light rain
            "1189": "rain.json",  # Moderate rain
            "1147": "cold-mist.json",  # Freezing fog
            "1135": "fog.json",  # Fog
            "1240": "rain.json",  # Light rain showers
            "1273": "thunderstorm.json",  # Thunderstorm
            "1213": "snow1.json",  # Snow
            "1222": "snow1.json",  # Moderate snow
            "1225": "snow1.json",  # Heavy snow
            "1258": "snow1.json",  # Snow showers
            "1210": "snow1.json",  # Light snow showers
            "1216": "snow1.json",  # Moderate snow showers
            "1219": "snow1.json",  # Moderate snow showers
            "1198": "rain.json",  # Light freezing rain
            "1087": "thunderstorm.json",  # Thunderstorm with rain
            "1117": "wind.json"  # Blizzard
        }

        def get_animation(condition_code):
            return animation_mapping.get(str(condition_code), "default.json")

        data['current']['animation_file'] = get_animation(data['current']['condition']['code'])

        for forecast in data['forecast']['forecastday']:
            forecast['day']['animation_file'] = get_animation(forecast['day']['condition']['code'])
            for hour in forecast['hour']:
                hour['animation_file'] = get_animation(hour['condition']['code'])

        data['sunrise'] = data['forecast']['forecastday'][0]['astro']['sunrise']
        data['sunset'] = data['forecast']['forecastday'][0]['astro']['sunset']
        data['moon_phase'] = data['forecast']['forecastday'][0]['astro']['moon_phase']

        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return {'message': 'City not found. Please ensure the city name is valid.'}

# Function to get city name using IP
def get_city_from_ip():
    try:
        response = requests.get(GEOLOCATION_API)
        response.raise_for_status()
        data = response.json()
        return data.get('city', 'Unknown Location')  # Default to "Unknown Location" if city not found
    except requests.exceptions.RequestException as e:
        print(f"Error fetching location from IP: {e}")
        return 'Unknown Location'
@app.before_request
def force_https():
    if not request.is_secure:
        return redirect(request.url.replace("http://", "https://"), code=301)
    
@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    city = None

    if request.method == 'POST':
        city = request.form['city'].strip()
        weather_data = get_weather(city)
    else:
        city = get_city_from_ip()
        weather_data = get_weather(city)

    return render_template('index.html', weather=weather_data, city=city)

if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.load_cert_chain('certs/cert.pem', 'certs/key.pem')
    app.run(host='0.0.0.0', port=5000, ssl_context=context)