"""
Task 4: Weather Information App - Service Layer
Description: Modular REST API service for fetching and parsing current weather data.
Supports OpenWeatherMap API with automatic fallback to Open-Meteo (zero-key API).
Handles HTTP errors, network timeouts, invalid cities, and JSON parsing gracefully.
"""

from datetime import datetime
import os
import requests
def load_env_file(filepath: str) -> None:
    """Safely load key-value pairs from a .env file into os.environ using Python standard library."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                for line in file:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#") and "=" in stripped:
                        key, val = stripped.split("=", 1)
                        key = key.strip()
                        val = val.strip().strip("\"'")
                        if key and key not in os.environ:
                            os.environ[key] = val
        except OSError:
            pass


# Automatically load local .env file on module import
_ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_env_file(_ENV_PATH)

# Constants & Default Timeouts
REQUEST_TIMEOUT = 10  # Seconds before aborting slow requests
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
OPEN_METEO_GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


# ---------------------------------------------------------------------------
# Custom Exceptions for Clear Error Categorization
# ---------------------------------------------------------------------------

class WeatherAPIError(Exception):
    """Base exception for weather API errors."""
    pass


class CityNotFoundError(WeatherAPIError):
    """Raised when the requested city cannot be found."""
    pass


class InvalidAPIKeyError(WeatherAPIError):
    """Raised when the provided API key is rejected (HTTP 401)."""
    pass


class NetworkTimeoutError(WeatherAPIError):
    """Raised when the network request exceeds timeout limit."""
    pass


class NetworkConnectionError(WeatherAPIError):
    """Raised when unable to reach the API server (offline / DNS failure)."""
    pass


# WMO Weather Code Mapping for Open-Meteo
WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def get_configured_api_key() -> str:
    """Retrieve the OpenWeatherMap API key from environment variable."""
    return os.environ.get("OPENWEATHER_API_KEY", "").strip()


def fetch_from_openweather(city: str, api_key: str) -> dict:
    """Fetch current weather from OpenWeatherMap REST API."""
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",  # Fetch Celsius temperature
    }

    try:
        response = requests.get(
            OPENWEATHER_BASE_URL,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.exceptions.Timeout:
        raise NetworkTimeoutError("The request timed out. Please check your internet connection.")
    except requests.exceptions.ConnectionError:
        raise NetworkConnectionError("Network error: Unable to connect to OpenWeatherMap server.")
    except requests.exceptions.RequestException as err:
        raise WeatherAPIError(f"Network error: {err}")

    # Handle HTTP status responses
    if response.status_code == 404:
        raise CityNotFoundError(f"City '{city}' was not found. Please check spelling.")
    if response.status_code == 401:
        raise InvalidAPIKeyError("Invalid OpenWeatherMap API key. Please check your .env configuration.")
    if response.status_code != 200:
        raise WeatherAPIError(f"API Error ({response.status_code}): {response.text}")

    try:
        data = response.json()
        return {
            "city": data.get("name", city.title()),
            "country": data.get("sys", {}).get("country", ""),
            "temp": round(data.get("main", {}).get("temp", 0.0), 1),
            "feels_like": round(data.get("main", {}).get("feels_like", 0.0), 1),
            "condition": data.get("weather", [{}])[0].get("main", "Clear"),
            "description": data.get("weather", [{}])[0].get("description", "clear sky").title(),
            "humidity": data.get("main", {}).get("humidity", 0),
            "wind_speed": round(data.get("wind", {}).get("speed", 0.0), 1),
            "pressure": data.get("main", {}).get("pressure", 0),
            "provider": "OpenWeatherMap",
            "timestamp": datetime.now().strftime("%I:%M %p, %b %d"),
        }
    except (KeyError, ValueError, TypeError) as err:
        raise WeatherAPIError(f"Failed to parse weather data: {err}")


def fetch_from_openmeteo(city: str) -> dict:
    """Fetch current weather using Open-Meteo API (requires NO API key)."""
    # Step 1: Geocoding city name to coordinates
    try:
        geo_resp = requests.get(
            OPEN_METEO_GEO_URL,
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.exceptions.Timeout:
        raise NetworkTimeoutError("Geocoding request timed out. Check your connection.")
    except requests.exceptions.ConnectionError:
        raise NetworkConnectionError("Unable to connect to weather geocoding service.")

    if geo_resp.status_code != 200:
        raise WeatherAPIError(f"Geocoding failed with status {geo_resp.status_code}")

    geo_data = geo_resp.json()
    results = geo_data.get("results")
    if not results:
        raise CityNotFoundError(f"City '{city}' was not found. Please check spelling.")

    first_hit = results[0]
    lat = first_hit.get("latitude")
    lon = first_hit.get("longitude")
    resolved_name = first_hit.get("name", city.title())
    country_code = first_hit.get("country_code", "").upper()

    # Step 2: Fetch current weather metrics
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,surface_pressure,wind_speed_10m",
        "wind_speed_unit": "ms",
    }

    try:
        weather_resp = requests.get(
            OPEN_METEO_WEATHER_URL,
            params=weather_params,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.exceptions.Timeout:
        raise NetworkTimeoutError("Weather forecast request timed out.")
    except requests.exceptions.ConnectionError:
        raise NetworkConnectionError("Unable to connect to weather forecast service.")

    if weather_resp.status_code != 200:
        raise WeatherAPIError(f"Weather lookup failed with status {weather_resp.status_code}")

    w_data = weather_resp.json()
    current = w_data.get("current", {})

    wmo_code = current.get("weather_code", 0)
    condition_desc = WMO_WEATHER_CODES.get(wmo_code, "Partly cloudy")

    return {
        "city": resolved_name,
        "country": country_code,
        "temp": round(current.get("temperature_2m", 0.0), 1),
        "feels_like": round(current.get("apparent_temperature", 0.0), 1),
        "condition": condition_desc,
        "description": condition_desc,
        "humidity": int(current.get("relative_humidity_2m", 0)),
        "wind_speed": round(current.get("wind_speed_10m", 0.0), 1),
        "pressure": int(current.get("surface_pressure", 1013)),
        "provider": "Open-Meteo (No-Key)",
        "timestamp": datetime.now().strftime("%I:%M %p, %b %d"),
    }


def get_weather(city_name: str) -> dict:
    """Unified entry point for weather retrieval.

    If an OpenWeatherMap API key is set in .env or environment, it uses OpenWeatherMap.
    Otherwise, it automatically uses Open-Meteo for immediate zero-setup functionality.
    """
    clean_city = city_name.strip()
    if not clean_city:
        raise ValueError("Please enter a valid city name.")

    api_key = get_configured_api_key()

    if api_key and api_key != "your_openweathermap_api_key_here":
        return fetch_from_openweather(clean_city, api_key)
    else:
        # Seamless zero-key fallback
        return fetch_from_openmeteo(clean_city)
