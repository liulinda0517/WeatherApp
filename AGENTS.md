# Agent Instructions for WeatherApp

This is a Flask-based weather dashboard that fetches real-time weather data from the OpenWeather API.

## 🚀 Quick Start

### Prerequisites
- **Environment Variable Required**: Set `OPENWEATHER_API_KEY` before running
  ```powershell
  $env:OPENWEATHER_API_KEY="your_api_key_here"
  ```
- Install dependencies: `pip install -r requirements.txt`
- Run app: `python app.py`
- Access at: `http://127.0.0.1:5000`

### Build & Run Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run in development mode
python app.py

# The app will be available at http://127.0.0.1:5000
```

## 🏗️ Architecture Overview

**Single-page Flask application with three main components:**

1. **Backend (`app.py`)**
   - `get_weather(city, units)`: Fetches weather data from OpenWeather API, transforms into a clean dictionary
   - `index()` route: Handles GET (displays form) and POST (processes search)
   - Unit support: `metric` (°C), `imperial` (°F), `standard` (K)
   - Error handling: API failures, invalid cities, missing credentials

2. **Frontend (`templates/index.html` + `static/css/app.css`)**
   - Form for city search and unit selection
   - Weather card displaying: temperature, "feels like", humidity, wind speed, pressure
   - Error message display
   - Responsive modern design

3. **Dependencies (`requirements.txt`)**
   - Flask: Web framework
   - requests: HTTP client for API calls
   - gunicorn: Production server

## 📋 Key Patterns & Conventions

### Error Handling
- **RuntimeError**: Missing API key (critical, halts execution)
- **ValueError**: Invalid city response from API
- **requests.RequestException**: API service unavailable
- All errors caught and displayed to user via template

### Unit Configuration
Units are defined in a dictionary structure for consistency:
```python
unit_config = {
    "metric": {"label": "°C", "wind": "m/s"},
    "imperial": {"label": "°F", "wind": "mph"},
    "standard": {"label": "K", "wind": "m/s"},
}
```
Always validate user input matches these keys.

### Data Flow
1. User submits form (city + units) → `index()` route
2. `get_weather()` fetches and transforms data
3. Template renders weather card with data
4. Weather icon fetched from OpenWeather CDN

### API Integration
- Base URL: `https://api.openweathermap.org/data/2.5/weather`
- Response validation: Check `response.json()["cod"] == 200`
- Field access uses `.get()` for optional fields (wind, sys)
- 10-second request timeout applied

## 🔒 Security Notes

- **API Key**: Stored in environment variables, never committed to git
- `.gitignore` should exclude any config files or credentials
- Flask debug mode is enabled (`debug=True`) — disable in production

## 📝 Common Development Tasks

### Adding a New Weather Field
1. Extract from API response in `get_weather()`
2. Add to returned dictionary
3. Display in `weather-card` section of `index.html`
4. Style in `app.css` if needed

### Modifying the UI
- Form and weather display are in `templates/index.html`
- Styling in `static/css/app.css`
- Use Jinja2 syntax for template variables (`{{ variable }}`)
- Error messages use `.error` class

### Testing Changes
- Always set `OPENWEATHER_API_KEY` before running
- Test with different cities, units, and error scenarios
- Verify error messages display correctly

## 📂 File Structure
```
WeatherApp/
├── app.py                 # Flask app with routes & API logic
├── requirements.txt       # Python dependencies
├── README.md             # User documentation
├── static/
│   └── css/
│       └── app.css       # Styling
└── templates/
    └── index.html        # Frontend HTML template
```

---

**Last Updated**: 2026-07-16
