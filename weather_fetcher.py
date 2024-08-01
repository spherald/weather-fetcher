import requests
import requests_cache
from retry_requests import retry
from datetime import datetime as dt
import openmeteo_requests

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

def geocode_city(city_name):
    geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        'name': city_name,
        'count': 1
    }
    try:
        response = requests.get(geocode_url, params=params)
        response.raise_for_status()
        data = response.json()
        if data and 'results' in data and len(data['results']) > 0:
            location = data['results'][0]
            return float(location['latitude']), float(location['longitude'])
        else:
            print("City not found")
            return None, None
    except requests.RequestException as e:
        print(f"Geocoding request failed: {e}")
        return None, None

def fetch_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "relative_humidity_2m", "weather_code"],
        "timezone": "auto"
    }
    try:
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        return response
    except Exception as e:
        print(f"Weather data request failed: {e}")
        return None

def weather_interpretation(weather_code):
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        51: "Light rain showers",
        61: "Light rain",
        71: "Light snow showers",
        80: "Light rain showers",
        95: "Thunderstorm",
        99: "Thunderstorm with hail"
    }
    return weather_codes.get(int(weather_code), "Unknown weather code")

def main():
    city_name = input("Enter city name: ")
    latitude, longitude = geocode_city(city_name)
    if latitude is None or longitude is None:
        return

    weather_data = fetch_weather(latitude, longitude)
    if weather_data is None:
        return

    current = weather_data.Current()
    temperature = current.Variables(0).Value()
    humidity = current.Variables(1).Value()
    weather_code = current.Variables(2).Value()
    current_time = dt.fromtimestamp(current.Time())
    formatted_time = current_time.strftime("%H:%M:%S %d-%m-%Y")

    print(f"Time and Date: {formatted_time}")
    print(f"Temperature: {temperature:.0f}°C")
    print(f"Humidity: {humidity:.0f}%")
    print(f"Description: {weather_interpretation(weather_code)}")

if __name__ == "__main__":
    main()