from flask import Flask, render_template, request, jsonify
import os
import time
import logging
from dotenv import load_dotenv
import requests
from collections import defaultdict

# ---------- Setup ----------
load_dotenv()
API_KEY = os.getenv("API_KEY")  # put API_KEY=your_key in .env
if not API_KEY:
    print("WARNING: API_KEY missing. Create a .env file with API_KEY=your_openweather_key")

app = Flask(__name__)

# Logging (basic error/info to app.log)
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

# Simple in-memory cache: {(city_lower, units): (timestamp, payload)}
CACHE_TTL = 300  # 5 minutes
_cache = {}

def _fetch_openweather(url, params):
    try:
        r = requests.get(url, params=params, timeout=12)
        data = r.json()
        return r.status_code, data
    except Exception as e:
        logging.exception("OpenWeather request failed")
        return 500, {"message": "Server error"}

def _aggregate_daily_from_3h_list(list_items, tz_offset):
    """
    Build a 5-day summary: for each calendar day (local to city), compute min/max temp
    and pick a representative icon (most frequent).
    """
    by_day = defaultdict(lambda: {"temps": [], "icons": []})
    for it in list_items:
        dt = it.get("dt", 0) + tz_offset
        # convert to local date (YYYY-MM-DD)
        day = time.strftime("%Y-%m-%d", time.gmtime(dt))
        main = it.get("main", {})
        weather = (it.get("weather") or [{}])[0]
        by_day[day]["temps"].append(main.get("temp"))
        by_day[day]["icons"].append(weather.get("icon"))

    daily = []
    for day, vals in sorted(by_day.items()):
        temps = [t for t in vals["temps"] if isinstance(t, (int, float))]
        if not temps:
            continue
        # pick most common icon
        icon_counts = defaultdict(int)
        for ic in vals["icons"]:
            icon_counts[ic] += 1
        icon = max(icon_counts, key=icon_counts.get)
        daily.append({
            "date": day,
            "min": round(min(temps), 1),
            "max": round(max(temps), 1),
            "icon": icon
        })
    # Keep next 5 days
    return daily[:5]

def _to_payload(current, forecast, units):
    # current
    sys = current.get("sys", {})
    main = current.get("main", {})
    wind = current.get("wind", {})
    weather = (current.get("weather") or [{}])[0]
    clouds = current.get("clouds", {}) or {}
    visibility = current.get("visibility")

    tz_offset = current.get("timezone", 0)  # seconds offset
    sunrise = sys.get("sunrise")
    sunset = sys.get("sunset")

    # Hourly: next 12 hours from forecast list (3h step = next 4 slots)
    # We'll take next 12 hours => next 4 entries in forecast.list
    hourly_items = (forecast.get("list") or [])[:4]
    hourly = []
    for it in hourly_items:
        w = (it.get("weather") or [{}])[0]
        hourly.append({
            "time": it.get("dt", 0) + forecast.get("city", {}).get("timezone", 0),
            "temp": round(it.get("main", {}).get("temp", 0), 1),
            "icon": w.get("icon"),
            "desc": w.get("description", "")
        })

    # Daily aggregation
    city_block = forecast.get("city", {}) or {}
    tz2 = city_block.get("timezone", tz_offset)
    daily = _aggregate_daily_from_3h_list(forecast.get("list", []), tz2)

    return {
        "units": units,  # 'metric' or 'imperial'
        "city": current.get("name"),
        "country": sys.get("country"),
        "coord": current.get("coord"),
        "now": {
            "temp": round(main.get("temp", 0), 1),
            "feels_like": round(main.get("feels_like", 0), 1),
            "pressure": main.get("pressure"),
            "humidity": main.get("humidity"),
            "visibility": visibility,
            "wind": wind.get("speed"),
            "clouds": clouds.get("all"),
            "icon": weather.get("icon"),
            "desc": weather.get("description", ""),
            "sunrise": sunrise,
            "sunset": sunset,
            "tz_offset": tz_offset
        },
        "hourly": hourly,
        "daily": daily
    }

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/weather", methods=["POST"])
def api_weather():
    body = request.get_json(silent=True) or {}
    city = (body.get("city") or "").strip()
    units = body.get("units") or "metric"  # 'metric' or 'imperial'
    if not city:
        return jsonify({"error": "City is required"}), 400

    cache_key = (city.lower(), units)
    now_ts = time.time()
    cached = _cache.get(cache_key)
    if cached and (now_ts - cached[0] < CACHE_TTL):
        return jsonify(cached[1])

    # 1) Current weather
    status1, cur = _fetch_openweather(CURRENT_URL, {
        "q": city,
        "appid": API_KEY,
        "units": units
    })
    if status1 != 200 or str(cur.get("cod")) != "200":
        msg = cur.get("message", "Unable to fetch current weather")
        logging.warning("Current weather fail for %s: %s", city, msg)
        return jsonify({"error": msg}), 404

    # 2) 5-day / 3-hour forecast
    status2, fc = _fetch_openweather(FORECAST_URL, {
        "q": city,
        "appid": API_KEY,
        "units": units
    })
    if status2 != 200 or str(fc.get("cod")) != "200":
        msg = fc.get("message", "Unable to fetch forecast")
        logging.warning("Forecast fail for %s: %s", city, msg)
        return jsonify({"error": msg}), 404

    payload = _to_payload(cur, fc, units)
    _cache[cache_key] = (now_ts, payload)
    return jsonify(payload)

if __name__ == "__main__":
    app.run(debug=True)
