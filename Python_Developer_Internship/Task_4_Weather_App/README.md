# Task 4: Weather Information App (GUI)

A modern, responsive desktop weather application built with Python 3, Tkinter, and REST APIs featuring non-blocking background threading, comprehensive error handling, and temperature unit conversion.

Developed as part of the **Auspify Technologies Python Developer Internship**.

---

## 📌 Project Overview

The **Weather Information App** allows users to look up real-time weather information for any city worldwide. It integrates with real weather REST APIs and parses JSON responses to display temperature, weather conditions, humidity, wind speed, and atmospheric pressure. 

To ensure a seamless user experience, all network requests are executed on background threads so that the **Tkinter desktop GUI remains 100% responsive and never freezes** during network latency or timeouts.

---

## ✨ Features

- **Real-Time Weather Metrics**:
  - City Name and ISO Country Code (e.g., `Mumbai, IN`, `London, GB`).
  - Current Temperature with one-click **°C / °F unit toggle**.
  - "Feels Like" apparent temperature.
  - Weather Condition description (e.g., *Clear sky, Scattered Clouds, Light Rain*).
  - Relative Humidity (`%`).
  - Wind Speed (`m/s`).
  - Atmospheric Pressure (`hPa`).
  - Observation timestamp.
- **Responsive Non-Blocking UI**:
  - Uses Python's `threading` module to run HTTP requests asynchronously.
  - Displays real-time loading feedback (*"Fetching real-time weather for..."*) while temporarily disabling the search button to prevent duplicate spam requests.
- **Dual REST API Engine**:
  - **OpenWeatherMap API**: Industry-standard provider supported via API key in `.env` or in-app dialog.
  - **Open-Meteo API (Zero-Key Fallback)**: Automatically active when no API key is set, enabling instant testing out of the box with zero waiting or signups.
- **Defensive Error Handling**:
  - Handles non-existent city names with clear, polite user guidance.
  - Catches network timeouts (`requests.exceptions.Timeout`) and connection drops (`requests.exceptions.ConnectionError`) gracefully without application crashes.
  - Validates empty strings and whitespace input.
- **Security & Secret Management**:
  - Keeps credentials strictly outside the codebase using `.env` and `.env.example`.
  - `.gitignore` prevents accidental commits of private API keys to GitHub.

---

## 🛠️ Prerequisites & Installation

1. **Python**: Version 3.8 or higher (Tested on Python 3.14).
2. **Install Required Packages**:
   Open your terminal in the workspace root and run:
   ```bash
   pip install -r Python_Developer_Internship/Task_4_Weather_App/requirements.txt
   ```

---

## 🔑 Weather API Setup Guide

This application provides two flexible options:

### Option 1: Instant Zero-Key Mode (Default)
No setup required! If `.env` is empty, the application automatically uses the **Open-Meteo REST API**, allowing you to search any city worldwide immediately.

### Option 2: OpenWeatherMap (Industry Standard)
1. Sign up for a free account at [openweathermap.org/appid](https://openweathermap.org/appid).
2. Copy your free API key from your account dashboard.
3. In `Task_4_Weather_App/`, copy `.env.example` to `.env`:
   ```bash
   cp Python_Developer_Internship/Task_4_Weather_App/.env.example Python_Developer_Internship/Task_4_Weather_App/.env
   ```
4. Paste your API key into `.env`:
   ```env
   OPENWEATHER_API_KEY=your_actual_api_key_here
   ```
*(Alternatively, you can click "Configure API Key" inside the running GUI to save it anytime.)*

---

## 🚀 How to Run the Application

Execute the following command in your terminal:

```bash
python Python_Developer_Internship/Task_4_Weather_App/main.py
```

### GUI Preview:

```text
+-------------------------------------------------------------+
|                   WEATHER INFORMATION PRO                   |
|       Real-time global weather insights powered by REST     |
+-------------------------------------------------------------+
|  Enter City: [ London                         ] [ Search ]  |
+-------------------------------------------------------------+
|                                                             |
|   London, GB                                                |
|   Observed: 12:10 AM, Oct 24                                |
|                                                             |
|   9.1 °C   [Switch to °F]                                   |
|   Overcast                                                  |
|   Feels like: 3.6 °C                                        |
|                                                             |
|   +--------------------------+--------------------------+   |
|   | Humidity: 67%            | Wind Speed: 7.6 m/s      |   |
|   +--------------------------+--------------------------+   |
|   | Pressure: 1001 hPa       | Data Provider: REST API  |   |
|   +--------------------------+--------------------------+   |
|                                                             |
|   [Status]: Success! Showing current weather for London.    |
+-------------------------------------------------------------+
```

---

## 🧪 Automated Testing & Verification

The test suite in `test_weather_app.py` contains **10 automated tests** covering offline mocked API responses, network timeout simulation, invalid city rejection, and real live API endpoints.

Run the tests with:

```bash
python Python_Developer_Internship/Task_4_Weather_App/test_weather_app.py -v
```

### Verified Test Results:

```text
test_temperature_unit_conversion ... ok
test_live_weather_fetch_invalid_city ... ok
test_live_weather_fetch_valid_city ... ok
test_empty_city_name_raises_value_error ... ok
test_network_connection_error_mocked ... ok
test_network_timeout_mocked ... ok
test_openmeteo_success_mocked ... ok
test_openweather_city_not_found_mocked ... ok
test_openweather_invalid_key_mocked ... ok
test_openweather_success_mocked ... ok

----------------------------------------------------------------------
Ran 10 tests in 3.545s

OK
```

---

## 📁 Project Structure

```text
Python_Developer_Internship/
├── Task_1_Password_Generator/
├── Task_2_Todo_List/
├── Task_3_Calculator_GUI/
└── Task_4_Weather_App/
    ├── main.py              # Tkinter GUI application & threaded event loop
    ├── weather_service.py   # REST API client & JSON parsing service
    ├── test_weather_app.py  # Unit tests (Mocked & Live tests)
    ├── requirements.txt     # Dependencies (requests, python-dotenv)
    ├── .env.example         # Template for API credentials
    ├── .gitignore           # Prevents committing .env and cache files
    └── README.md            # Comprehensive documentation
```

---

## 🎯 Technical Decisions & Interview Talking Points

1. **Why use Multi-Threading (`threading.Thread`) in a Tkinter GUI?**
   Tkinter operates on a single-threaded event loop (`mainloop()`). If a synchronous network request (`requests.get`) takes 2–5 seconds due to network latency, the entire window freezes, becoming unresponsive ("Not Responding" in Windows). Spawning a background daemon thread and passing results back via `root.after(0, callback)` keeps the interface completely smooth and responsive.

2. **Why provide a dual-API fallback architecture?**
   OpenWeatherMap keys typically require 10 to 30 minutes after registration to activate on the provider's CDN. Having an automatic fallback to Open-Meteo ensures the applicant can immediately test and demonstrate the app during a live interview without external blockers.

3. **How are HTTP errors handled?**
   Rather than letting raw HTTP exceptions bubble up and crash the application, the service layer maps HTTP status codes (`404` -> `CityNotFoundError`, `401` -> `InvalidAPIKeyError`, `Timeout` -> `NetworkTimeoutError`) into domain-specific exceptions with friendly user messages.
