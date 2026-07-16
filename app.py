from flask import Flask, render_template, request
import os
import requests
from datetime import datetime

app = Flask(__name__)

API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"
AIR_POLLUTION_BASE_URL = "https://api.openweathermap.org/data/2.5/air_pollution"


def get_weather(city: str, units: str = "metric"):
    if not API_KEY:
        raise RuntimeError("Missing OpenWeather API key. Set OPENWEATHER_API_KEY before running the app.")

    unit_config = {
        "metric": {"label": "°C", "wind": "m/s"},
        "imperial": {"label": "°F", "wind": "mph"},
        "standard": {"label": "K", "wind": "m/s"},
    }

    selected_units = unit_config.get(units, unit_config["metric"])

    params = {
        "q": city,
        "appid": API_KEY,
        "units": units,
    }

    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if data.get("cod") != 200:
        raise ValueError(data.get("message", "Unable to fetch weather for that city."))

    weather = data["weather"][0]
    main = data["main"]
    wind = data.get("wind", {})

    return {
        "city": data["name"],
        "country": data.get("sys", {}).get("country", ""),
        "temperature": round(main["temp"]),
        "feels_like": round(main.get("feels_like", main["temp"])),
        "description": weather["description"].title(),
        "icon": weather["icon"],
        "humidity": main.get("humidity"),
        "wind_speed": wind.get("speed"),
        "pressure": main.get("pressure"),
        "unit_symbol": selected_units["label"],
        "wind_unit": selected_units["wind"],
        "lat": data.get("coord", {}).get("lat"),
        "lon": data.get("coord", {}).get("lon"),
    }


def get_forecast(city: str, units: str = "metric"):
    """Fetch 5-day forecast and aggregate into daily summaries."""
    if not API_KEY:
        raise RuntimeError("Missing OpenWeather API key.")

    params = {
        "q": city,
        "appid": API_KEY,
        "units": units,
    }

    response = requests.get(FORECAST_BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if data.get("cod") != "200":
        raise ValueError("Unable to fetch forecast data.")

    # Group forecasts by day (API returns 40 items of 3-hour forecasts = 5 days)
    daily_forecasts = {}
    
    for item in data["list"]:
        dt = datetime.fromtimestamp(item["dt"])
        day_key = dt.strftime("%Y-%m-%d")
        
        if day_key not in daily_forecasts:
            daily_forecasts[day_key] = {
                "date": dt.strftime("%a, %b %d"),
                "temps": [],
                "conditions": [],
                "icons": [],
                "rain_chances": [],
            }
        
        daily_forecasts[day_key]["temps"].append(item["main"]["temp"])
        daily_forecasts[day_key]["rain_chances"].append(item.get("pop", 0) * 100)
        
        # Get primary weather condition
        if item.get("weather"):
            daily_forecasts[day_key]["conditions"].append(item["weather"][0]["description"])
            daily_forecasts[day_key]["icons"].append(item["weather"][0]["icon"])

    # Aggregate daily data
    forecast_list = []
    for day_key in sorted(daily_forecasts.keys())[:5]:  # Only first 5 days
        day_data = daily_forecasts[day_key]
        
        forecast_list.append({
            "date": day_data["date"],
            "high_temp": round(max(day_data["temps"])),
            "low_temp": round(min(day_data["temps"])),
            "condition": day_data["conditions"][0].title() if day_data["conditions"] else "Unknown",
            "icon": day_data["icons"][0] if day_data["icons"] else "01d",
            "precipitation": round(sum(day_data["rain_chances"]) / len(day_data["rain_chances"])),
        })

    return forecast_list


def get_air_quality(lat: float, lon: float):
    """Fetch air quality data including AQI and pollutants."""
    if not API_KEY:
        raise RuntimeError("Missing OpenWeather API key.")

    # AQI level mapping (1-5)
    aqi_mapping = {
        1: {"label": "Good", "color": "#22c55e", "advice": "Air quality is satisfactory."},
        2: {"label": "Fair", "color": "#eab308", "advice": "Acceptable air quality for most."},
        3: {"label": "Moderate", "color": "#f97316", "advice": "Sensitive groups may be affected."},
        4: {"label": "Poor", "color": "#ef4444", "advice": "Everyone may be affected. Reduce outdoor activity."},
        5: {"label": "Very Poor", "color": "#a855f7", "advice": "Avoid outdoor activity. Wear protection."},
    }

    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
    }

    response = requests.get(AIR_POLLUTION_BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if not data.get("list"):
        raise ValueError("Unable to fetch air quality data.")

    # Get the first (current) air quality data point
    current = data["list"][0]
    main = current.get("main", {})
    components = current.get("components", {})

    aqi_level = main.get("aqi", 3)  # Default to Moderate if not available
    aqi_info = aqi_mapping.get(aqi_level, aqi_mapping[3])

    return {
        "aqi_level": aqi_level,
        "aqi_label": aqi_info["label"],
        "aqi_color": aqi_info["color"],
        "aqi_advice": aqi_info["advice"],
        "pm25": round(components.get("pm2_5", 0), 1),
        "pm10": round(components.get("pm10", 0), 1),
        "o3": round(components.get("o3", 0), 1),
        "no2": round(components.get("no2", 0), 1),
    }


@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
    forecast = None
    air_quality = None
    error = None
    city = ""
    units = "metric"

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        units = request.form.get("units", "metric").strip().lower()
        if units not in {"metric", "imperial", "standard"}:
            units = "metric"

        if not city:
            error = "Please enter a city name."
        else:
            try:
                weather = get_weather(city, units)
                # Fetch forecast only if current weather succeeds
                try:
                    forecast = get_forecast(city, units)
                except Exception as forecast_error:
                    # Log forecast error but don't stop app - current weather still shows
                    print(f"Forecast error: {forecast_error}")
                    forecast = None
                
                # Fetch air quality only if coordinates available
                if weather and weather.get("lat") and weather.get("lon"):
                    try:
                        air_quality = get_air_quality(weather["lat"], weather["lon"])
                    except Exception as aqi_error:
                        # Log AQI error but don't stop app - current weather still shows
                        print(f"Air quality error: {aqi_error}")
                        air_quality = None
            except requests.RequestException:
                error = "Weather service is unavailable right now. Please try again later."
            except ValueError as exc:
                error = str(exc)
            except RuntimeError as exc:
                error = str(exc)

    return render_template("index.html", weather=weather, forecast=forecast, air_quality=air_quality, city=city, error=error, units=units)


if __name__ == "__main__":
    app.run(debug=True)
