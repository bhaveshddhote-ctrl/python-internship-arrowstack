"""
Task 4: Weather Information App (GUI)
Internship Project: Auspify Technologies Python Developer Internship
Description: A modern desktop weather application with non-blocking threading,
real-time REST API integration, and comprehensive error handling.
Built with Python 3, Tkinter, and the requests library following PEP 8.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox

# Add current directory to module search path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import weather_service


# ---------------------------------------------------------------------------
# UI Theme & Styling Palette (Modern Deep Ocean Theme)
# ---------------------------------------------------------------------------

THEME = {
    "bg_app": "#0f172a",          # Deep slate background
    "bg_card": "#1e293b",         # Card background
    "bg_card_inner": "#334155",   # Metric tile background
    "bg_input": "#1e293b",        # Search entry background
    "txt_main": "#f8fafc",        # Main white text
    "txt_muted": "#94a3b8",       # Subtle gray text
    "accent_blue": "#38bdf8",     # Cyan / Sky blue
    "accent_blue_hover": "#0284c7",
    "accent_green": "#4ade80",    # Mint green
    "accent_orange": "#fb923c",   # Warm peach
    "accent_red": "#f87171",      # Soft red
}


class WeatherApp:
    """Professional Weather Application GUI."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Weather Information Pro")
        self.root.geometry("460x640")
        self.root.minsize(420, 580)
        self.root.configure(bg=THEME["bg_app"])

        # Temperature Unit State (Celsius or Fahrenheit)
        self.current_unit = "C"
        self.last_weather_data = None

        self._build_header()
        self._build_search_bar()
        self._build_status_bar()
        self._build_weather_card()
        self._build_footer()

        # Fetch a default city on startup
        self.root.after(100, lambda: self.search_city("Mumbai"))

    def _build_header(self):
        """Build top application title."""
        header_frame = tk.Frame(self.root, bg=THEME["bg_app"])
        header_frame.pack(fill="x", padx=20, pady=(18, 10))

        title_label = tk.Label(
            header_frame,
            text="Weather Information Pro",
            font=("Segoe UI", 18, "bold"),
            fg=THEME["txt_main"],
            bg=THEME["bg_app"],
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            header_frame,
            text="Real-time global weather insights powered by REST APIs",
            font=("Segoe UI", 9),
            fg=THEME["txt_muted"],
            bg=THEME["bg_app"],
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))

    def _build_search_bar(self):
        """Build search entry bar and action button."""
        search_frame = tk.Frame(self.root, bg=THEME["bg_app"])
        search_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.city_entry_var = tk.StringVar(value="")
        self.city_entry = tk.Entry(
            search_frame,
            textvariable=self.city_entry_var,
            font=("Segoe UI", 12),
            bg=THEME["bg_card"],
            fg=THEME["txt_main"],
            insertbackground=THEME["txt_main"],
            relief="flat",
            bd=8,
        )
        self.city_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.city_entry.bind("<Return>", lambda event: self._on_search_clicked())

        self.search_btn = tk.Button(
            search_frame,
            text="Search",
            font=("Segoe UI", 11, "bold"),
            bg=THEME["accent_blue"],
            fg="#0f172a",
            activebackground=THEME["accent_blue_hover"],
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=16,
            pady=6,
            cursor="hand2",
            command=self._on_search_clicked,
        )
        self.search_btn.pack(side="right")

    def _build_status_bar(self):
        """Build message status banner."""
        self.status_var = tk.StringVar(value="Ready. Enter a city name above.")
        self.status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Segoe UI", 10),
            fg=THEME["txt_muted"],
            bg=THEME["bg_app"],
            wraplength=400,
        )
        self.status_label.pack(fill="x", padx=20, pady=(0, 8))

    def _build_weather_card(self):
        """Build main weather data card."""
        self.card_frame = tk.Frame(self.root, bg=THEME["bg_card"], padx=20, pady=18)
        self.card_frame.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        # Location & Timestamp Line
        self.location_var = tk.StringVar(value="--")
        self.location_label = tk.Label(
            self.card_frame,
            textvariable=self.location_var,
            font=("Segoe UI", 18, "bold"),
            fg=THEME["txt_main"],
            bg=THEME["bg_card"],
        )
        self.location_label.pack(anchor="w")

        self.timestamp_var = tk.StringVar(value="")
        self.timestamp_label = tk.Label(
            self.card_frame,
            textvariable=self.timestamp_var,
            font=("Segoe UI", 9),
            fg=THEME["txt_muted"],
            bg=THEME["bg_card"],
        )
        self.timestamp_label.pack(anchor="w", pady=(0, 8))

        # Temperature & Condition Header Frame
        temp_row = tk.Frame(self.card_frame, bg=THEME["bg_card"])
        temp_row.pack(fill="x", pady=(4, 10))

        self.temp_var = tk.StringVar(value="-- °C")
        self.temp_label = tk.Label(
            temp_row,
            textvariable=self.temp_var,
            font=("Segoe UI", 36, "bold"),
            fg=THEME["accent_blue"],
            bg=THEME["bg_card"],
        )
        self.temp_label.pack(side="left")

        # Unit Toggle Button (°C / °F)
        self.unit_btn = tk.Button(
            temp_row,
            text="Switch to °F",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["bg_card_inner"],
            fg=THEME["txt_main"],
            relief="flat",
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self._toggle_unit,
        )
        self.unit_btn.pack(side="right", padx=(8, 0))

        self.condition_var = tk.StringVar(value="--")
        self.condition_label = tk.Label(
            self.card_frame,
            textvariable=self.condition_var,
            font=("Segoe UI", 13, "bold"),
            fg=THEME["accent_green"],
            bg=THEME["bg_card"],
        )
        self.condition_label.pack(anchor="w")

        self.feels_like_var = tk.StringVar(value="Feels like: --")
        self.feels_like_label = tk.Label(
            self.card_frame,
            textvariable=self.feels_like_var,
            font=("Segoe UI", 10),
            fg=THEME["txt_muted"],
            bg=THEME["bg_card"],
        )
        self.feels_like_label.pack(anchor="w", pady=(0, 16))

        # Grid of Additional Metrics
        metrics_grid = tk.Frame(self.card_frame, bg=THEME["bg_card"])
        metrics_grid.pack(fill="x")
        metrics_grid.columnconfigure(0, weight=1)
        metrics_grid.columnconfigure(1, weight=1)

        self.humidity_var = tk.StringVar(value="--")
        self._build_metric_tile(metrics_grid, 0, 0, "Humidity", self.humidity_var)

        self.wind_var = tk.StringVar(value="--")
        self._build_metric_tile(metrics_grid, 0, 1, "Wind Speed", self.wind_var)

        self.pressure_var = tk.StringVar(value="--")
        self._build_metric_tile(metrics_grid, 1, 0, "Air Pressure", self.pressure_var)

        self.provider_var = tk.StringVar(value="--")
        self._build_metric_tile(metrics_grid, 1, 1, "Data Provider", self.provider_var)

    def _build_metric_tile(self, parent, row, col, title, string_var):
        """Helper to create a neat 2-line metric tile."""
        tile = tk.Frame(parent, bg=THEME["bg_card_inner"], padx=12, pady=10)
        tile.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        lbl_title = tk.Label(
            tile,
            text=title,
            font=("Segoe UI", 9),
            fg=THEME["txt_muted"],
            bg=THEME["bg_card_inner"],
        )
        lbl_title.pack(anchor="w")

        lbl_val = tk.Label(
            tile,
            textvariable=string_var,
            font=("Segoe UI", 12, "bold"),
            fg=THEME["txt_main"],
            bg=THEME["bg_card_inner"],
        )
        lbl_val.pack(anchor="w", pady=(2, 0))

    def _build_footer(self):
        """Build bottom settings & help links."""
        footer_frame = tk.Frame(self.root, bg=THEME["bg_app"])
        footer_frame.pack(fill="x", padx=20, pady=(0, 14))

        api_btn = tk.Button(
            footer_frame,
            text="Configure API Key",
            font=("Segoe UI", 9, "underline"),
            bg=THEME["bg_app"],
            fg=THEME["accent_blue"],
            activebackground=THEME["bg_app"],
            activeforeground=THEME["accent_blue_hover"],
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self._show_api_key_dialog,
        )
        api_btn.pack(side="left")

        quick_label = tk.Label(
            footer_frame,
            text="Try: London, Tokyo, New York, Delhi",
            font=("Segoe UI", 8),
            fg=THEME["txt_muted"],
            bg=THEME["bg_app"],
        )
        quick_label.pack(side="right")

    # -----------------------------------------------------------------------
    # Asynchronous Request Handling (Zero UI Freeze)
    # -----------------------------------------------------------------------

    def _on_search_clicked(self):
        """Validate input and trigger background fetch thread."""
        city = self.city_entry_var.get().strip()
        if not city:
            self._display_error("Please enter a city name to search.")
            return

        self.search_city(city)

    def search_city(self, city_name: str):
        """Spawn background worker thread for API request."""
        # Set loading state
        self.search_btn.config(state="disabled", text="Loading...")
        self.status_var.set(f"Fetching real-time weather for '{city_name}'...")
        self.status_label.config(fg=THEME["accent_blue"])

        # Run network call in daemon thread
        thread = threading.Thread(
            target=self._worker_fetch_weather,
            args=(city_name,),
            daemon=True,
        )
        thread.start()

    def _worker_fetch_weather(self, city_name: str):
        """Worker function running in separate thread."""
        try:
            data = weather_service.get_weather(city_name)
            # Send result back to main GUI thread
            self.root.after(0, self._handle_weather_success, data)
        except weather_service.CityNotFoundError as err:
            self.root.after(0, self._display_error, str(err))
        except weather_service.InvalidAPIKeyError as err:
            self.root.after(0, self._display_error, str(err))
        except weather_service.NetworkTimeoutError as err:
            self.root.after(0, self._display_error, str(err))
        except weather_service.NetworkConnectionError as err:
            self.root.after(0, self._display_error, str(err))
        except Exception as err:
            self.root.after(0, self._display_error, f"Unexpected error: {err}")

    def _handle_weather_success(self, data: dict):
        """Update GUI elements with fetched weather data."""
        self.search_btn.config(state="normal", text="Search")
        self.last_weather_data = data

        location_text = f"{data['city']}, {data['country']}" if data.get("country") else data['city']
        self.location_var.set(location_text)
        self.timestamp_var.set(f"Observed: {data['timestamp']}")
        self.condition_var.set(data['description'])

        self._refresh_temperature_display()

        self.humidity_var.set(f"{data['humidity']}%")
        self.wind_var.set(f"{data['wind_speed']} m/s")
        self.pressure_var.set(f"{data['pressure']} hPa")
        self.provider_var.set(data.get("provider", "REST API"))

        self.status_var.set(f"Success! Showing current weather for {data['city']}.")
        self.status_label.config(fg=THEME["accent_green"])

    def _display_error(self, message: str):
        """Display error banner and re-enable UI."""
        self.search_btn.config(state="normal", text="Search")
        self.status_var.set(f"Error: {message}")
        self.status_label.config(fg=THEME["accent_red"])

    def _refresh_temperature_display(self):
        """Refresh temperature labels based on active unit (C / F)."""
        if not self.last_weather_data:
            return

        temp_c = self.last_weather_data["temp"]
        feels_c = self.last_weather_data["feels_like"]

        if self.current_unit == "C":
            self.temp_var.set(f"{temp_c} °C")
            self.feels_like_var.set(f"Feels like: {feels_c} °C")
            self.unit_btn.config(text="Switch to °F")
        else:
            temp_f = round((temp_c * 9 / 5) + 32, 1)
            feels_f = round((feels_c * 9 / 5) + 32, 1)
            self.temp_var.set(f"{temp_f} °F")
            self.feels_like_var.set(f"Feels like: {feels_f} °F")
            self.unit_btn.config(text="Switch to °C")

    def _toggle_unit(self):
        """Toggle between Celsius and Fahrenheit."""
        self.current_unit = "F" if self.current_unit == "C" else "C"
        self._refresh_temperature_display()

    def _show_api_key_dialog(self):
        """Open a modal dialog to let user configure their OpenWeatherMap API key."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Configure API Key")
        dialog.geometry("380x220")
        dialog.configure(bg=THEME["bg_card"])
        dialog.transient(self.root)
        dialog.grab_set()

        lbl = tk.Label(
            dialog,
            text="OpenWeatherMap API Key Settings",
            font=("Segoe UI", 12, "bold"),
            fg=THEME["txt_main"],
            bg=THEME["bg_card"],
        )
        lbl.pack(pady=(16, 6))

        info = tk.Label(
            dialog,
            text="If left empty, the app automatically uses\nOpen-Meteo with zero setup needed.",
            font=("Segoe UI", 9),
            fg=THEME["txt_muted"],
            bg=THEME["bg_card"],
            justify="center",
        )
        info.pack(pady=(0, 10))

        key_var = tk.StringVar(value=weather_service.get_configured_api_key())
        entry = tk.Entry(
            dialog,
            textvariable=key_var,
            font=("Segoe UI", 10),
            bg=THEME["bg_app"],
            fg=THEME["txt_main"],
            insertbackground=THEME["txt_main"],
            width=36,
        )
        entry.pack(pady=(0, 16))

        def save_key():
            new_key = key_var.get().strip()
            os.environ["OPENWEATHER_API_KEY"] = new_key
            env_path = os.path.join(CURRENT_DIR, ".env")
            try:
                with open(env_path, "w", encoding="utf-8") as f:
                    f.write(f"OPENWEATHER_API_KEY={new_key}\n")
                messagebox.showinfo("Saved", "API Key saved successfully to .env!", parent=dialog)
            except Exception as e:
                messagebox.showwarning("Notice", f"Applied for current session ({e})", parent=dialog)
            dialog.destroy()

        btn_save = tk.Button(
            dialog,
            text="Save Configuration",
            font=("Segoe UI", 10, "bold"),
            bg=THEME["accent_blue"],
            fg="#0f172a",
            relief="flat",
            command=save_key,
        )
        btn_save.pack()


def main():
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
