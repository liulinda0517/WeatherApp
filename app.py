from flask import Flask, render_template, request
import os
import requests

app = Flask(__name__)

API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


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
    }


@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
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
            except requests.RequestException:
                error = "Weather service is unavailable right now. Please try again later."
            except ValueError as exc:
                error = str(exc)
            except RuntimeError as exc:
                error = str(exc)

    return render_template("index.html", weather=weather, city=city, error=error, units=units)


if __name__ == "__main__":
    app.run(debug=True)
