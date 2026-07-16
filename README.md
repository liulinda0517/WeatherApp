# 🌤 WeatherApp

A modern Flask weather dashboard that retrieves real-time weather information using the OpenWeather API.

---

## 📌 Features

- Search weather by city
- Display current temperature
- Feels-like temperature
- Humidity
- Wind speed
- Atmospheric pressure
- Weather icon
- Celsius / Fahrenheit / Kelvin support
- Error handling for invalid city names
- Responsive modern interface

---

## 🛠 Tech Stack

- Python
- Flask
- HTML
- CSS
- Requests
- OpenWeather API
- Git
- GitHub

---

## 📁 Project Structure

```text
WeatherApp/
├── static/
│   └── css/
│       └── app.css
├── templates/
│   └── index.html
├── .gitignore
├── app.py
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Install dependencies

```bash
pip install -r requirements.txt
```

### Set your API Key

PowerShell

```powershell
$env:OPENWEATHER_API_KEY="your_api_key_here"
```

### Run the application

```bash
python app.py
```

Open your browser:

```
http://127.0.0.1:5000
```

---

## 🌦 Example Information Displayed

- City
- Country
- Temperature
- Feels Like
- Humidity
- Wind Speed
- Pressure
- Weather Icon

---

## 🔒 Security

The OpenWeather API key is stored using environment variables and is **not uploaded to GitHub**.

---

## 👩‍💻 Author

**Tsailing Liu**