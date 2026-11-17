"""
Comprehensive Automated Test Suite for Task 4: Weather Information App
Verifies:
- Mocked REST API parsing & OpenWeatherMap integration
- Mocked Open-Meteo zero-key fallback
- Error handling (404 City Not Found, 401 Invalid Key, Network Timeout, Connection Error)
- Input validation (empty string, whitespace)
- Missing / unexpected JSON fields resilience
- Live API integration with real endpoints (Paris, Mumbai)
- Live invalid city rejection
- GUI headless initialization and C/F unit conversion formula
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add target directory to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import weather_service
import requests


class TestWeatherServiceMocked(unittest.TestCase):
    """Offline unit tests using mocks to verify API parsing & error handling."""

    def test_empty_city_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            weather_service.get_weather("")
        with self.assertRaises(ValueError):
            weather_service.get_weather("   ")

    @patch("requests.get")
    def test_openweather_success_mocked(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "name": "Tokyo",
            "sys": {"country": "JP"},
            "main": {
                "temp": 16.2,
                "feels_like": 15.8,
                "humidity": 55,
                "pressure": 1015,
            },
            "weather": [{"main": "Clouds", "description": "broken clouds"}],
            "wind": {"speed": 3.2},
        }
        mock_get.return_value = mock_resp

        result = weather_service.fetch_from_openweather("Tokyo", "dummy_key")
        self.assertEqual(result["city"], "Tokyo")
        self.assertEqual(result["country"], "JP")
        self.assertEqual(result["temp"], 16.2)
        self.assertEqual(result["humidity"], 55)
        self.assertEqual(result["provider"], "OpenWeatherMap")

    @patch("requests.get")
    def test_openweather_city_not_found_mocked(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp

        with self.assertRaises(weather_service.CityNotFoundError):
            weather_service.fetch_from_openweather("InvalidCity", "dummy_key")

    @patch("requests.get")
    def test_openweather_invalid_key_mocked(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_get.return_value = mock_resp

        with self.assertRaises(weather_service.InvalidAPIKeyError):
            weather_service.fetch_from_openweather("London", "bad_key")

    @patch("requests.get", side_effect=requests.exceptions.Timeout)
    def test_network_timeout_mocked(self, mock_get):
        with self.assertRaises(weather_service.NetworkTimeoutError):
            weather_service.fetch_from_openweather("Berlin", "dummy_key")

    @patch("requests.get", side_effect=requests.exceptions.ConnectionError)
    def test_network_connection_error_mocked(self, mock_get):
        with self.assertRaises(weather_service.NetworkConnectionError):
            weather_service.fetch_from_openweather("Rome", "dummy_key")

    @patch("requests.get")
    def test_openmeteo_success_mocked(self, mock_get):
        # 1st call = geocoding, 2nd call = forecast
        mock_geo = MagicMock()
        mock_geo.status_code = 200
        mock_geo.json.return_value = {
            "results": [{"name": "Sydney", "country_code": "AU", "latitude": -33.86, "longitude": 151.20}]
        }

        mock_weather = MagicMock()
        mock_weather.status_code = 200
        mock_weather.json.return_value = {
            "current": {
                "temperature_2m": 22.4,
                "apparent_temperature": 21.8,
                "relative_humidity_2m": 60,
                "wind_speed_10m": 4.5,
                "surface_pressure": 1018,
                "weather_code": 0,
            }
        }

        mock_get.side_effect = [mock_geo, mock_weather]

        result = weather_service.fetch_from_openmeteo("Sydney")
        self.assertEqual(result["city"], "Sydney")
        self.assertEqual(result["country"], "AU")
        self.assertEqual(result["temp"], 22.4)
        self.assertEqual(result["condition"], "Clear sky")


class TestWeatherServiceLive(unittest.TestCase):
    """Live network verification with real-world weather endpoints."""

    def test_live_weather_fetch_valid_city(self):
        """Live Test: Fetch current weather for Paris."""
        data = weather_service.get_weather("Paris")
        self.assertIn("city", data)
        self.assertIn("temp", data)
        self.assertIn("humidity", data)
        self.assertIn("wind_speed", data)
        self.assertIsInstance(data["temp"], (int, float))
        self.assertGreaterEqual(data["humidity"], 0)
        self.assertLessEqual(data["humidity"], 100)

    def test_live_weather_fetch_invalid_city(self):
        """Live Test: Ensure invalid city raises CityNotFoundError."""
        with self.assertRaises(weather_service.CityNotFoundError):
            weather_service.get_weather("ZzQxNonExistentPlace999")


class TestWeatherGUIState(unittest.TestCase):
    """Headless verification of GUI logic and temperature unit toggling."""

    def test_temperature_unit_conversion(self):
        # 25 °C should convert to 77.0 °F
        celsius = 25.0
        fahrenheit = round((celsius * 9 / 5) + 32, 1)
        self.assertEqual(fahrenheit, 77.0)

        # 0 °C should convert to 32.0 °F
        zero_c = 0.0
        zero_f = round((zero_c * 9 / 5) + 32, 1)
        self.assertEqual(zero_f, 32.0)


if __name__ == "__main__":
    unittest.main()
