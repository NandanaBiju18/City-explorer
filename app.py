import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
load_dotenv()
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

def get_city_info(city):
    try:
        search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{city}_(city)"
        response = requests.get(search_url, headers={"User-Agent": "CityExplorer/1.0"})

        # fallback if city_(city) fails
        if response.status_code != 200:
            search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{city}"
            response = requests.get(search_url, headers={"User-Agent": "CityExplorer/1.0"})

        if response.status_code != 200:
            return {
                "title": city,
                "summary": f"{city} is a city in India known for its culture and tourism.",
                "image": None
            }

        data = response.json()

        return {
            "title": data.get("title", city),
            "summary": data.get("extract", ""),
            "image": data.get("thumbnail", {}).get("source")
        }

    except:
        return {
            "title": city,
            "summary": f"{city} is a culturally important city in India.",
            "image": None
        }

def get_tourist_places(lat, lon):

    url = (
        f"https://api.geoapify.com/v2/places"
        f"?categories=tourism.attraction"
        f"&filter=circle:{lon},{lat},50000"
        f"&limit=20"
        f"&apiKey={GEOAPIFY_API_KEY}"
    )

    response = requests.get(url).json()

    places = []

    for place in response.get("features", []):

        props = place["properties"]
        name = props.get("name", "")

        if (
            name
            and "shop" not in name.lower()
            and "store" not in name.lower()
            and "grocery" not in name.lower()
        ):
            places.append(name)

    return list(set(places))

def get_location_details(lat, lon):

    url = (
        f"https://api.geoapify.com/v1/geocode/reverse"
        f"?lat={lat}&lon={lon}&apiKey={GEOAPIFY_API_KEY}"
    )

    data = requests.get(url).json()

    if not data.get("features"):
        return {
            "state": "Unknown",
            "country": "Unknown"
        }

    props = data["features"][0]["properties"]

    return {
        "state": (
            props.get("state")
            or props.get("region")
            or props.get("state_district")
            or props.get("county")
            or "Unknown"
        ),
        "country": props.get("country", "Unknown")
    }


# 🧠 Smart summary logic
def city_summary(city, weather_desc, temp):
    if "rain" in weather_desc:
        vibe = "cool and rainy, great for indoor experiences"
    elif temp > 30:
        vibe = "hot and energetic, perfect for outdoor travel"
    elif temp < 15:
        vibe = "cold and calm, ideal for cozy exploration"
    else:
        vibe = "pleasant and balanced for tourism"

    return f"{city.title()} is a {vibe} city with diverse culture and lifestyle."

def get_weather(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    response = requests.get(url).json()

    print(response)

    if "sys" not in response:
        return {
            "temp": 0,
            "desc": "Unavailable",
            "humidity": 0,
            "lat": 0,
            "lon": 0,
            "country": "Unknown"
        }

    country_codes = {
        "IN": "India",
        "US": "United States",
        "GB": "United Kingdom",
        "FR": "France"
    }

    country = country_codes.get(
        response["sys"]["country"],
        response["sys"]["country"]
    )

    return {
        "temp": response["main"]["temp"],
        "desc": response["weather"][0]["description"],
        "humidity": response["main"]["humidity"],
        "lat": response["coord"]["lat"],
        "lon": response["coord"]["lon"],
        "timezone": response["timezone"],
        "country": country
    }

def get_news(city):
    api_key = os.getenv("NEWS_API_KEY")

    queries = [
        city,
        f"{city} India",
        "Kerala news",
        "India local news"
    ]

    articles = []

    for q in queries:
        url = (
            "https://newsapi.org/v2/everything?"
            f"q={q}&sortBy=publishedAt&pageSize=5&apiKey={api_key}"
        )

        response = requests.get(url).json()
        articles += response.get("articles", [])

        if len(articles) >= 5:
            break

    if not articles:
        return [{
            "title": "No recent news found",
            "description": "Try a bigger city or broader region",
            "source": "System",
            "url": ""
        }]

    return [
        {
            "title": a["title"],
            "description": a.get("description", ""),
            "source": a["source"]["name"],
            "url": a.get("url", "")
        }
        for a in articles[:5]
    ]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/city-data", methods=["POST"])
def city_data():
    data = request.json
    city = data["city"]

    weather = get_weather(city)

    temp = weather["temp"]
    desc = weather["desc"]
    lat = weather["lat"]
    lon = weather["lon"]
    timezone = weather["timezone"]

    summary = city_summary(city, desc, temp)
    intro = ai_place_intro(city, desc, temp)

    city_info = get_city_info(city)
    location = get_location_details(lat, lon)
    country_info = get_country_info(weather["country"])
    places = get_tourist_places(lat, lon)
    news = get_news(city)
    print(location)

    from datetime import datetime, timezone, timedelta

    offset = weather["timezone"]

    local_time = datetime.now(
        timezone.utc
    ) + timedelta(seconds=offset)

    city_language = get_city_language(
        location["state"],
        location["country"]
    )

    return jsonify({
        "city": city,
        "country": weather["country"],
        "temp": temp,
        "desc": desc,
        "humidity": weather["humidity"],
        "summary": summary,
        "intro": intro,
        "lat": lat,
        "lon": lon,
        "places": places,
        "news": news,
        "wiki_title": city_info["title"],
        "wiki_summary": city_info["summary"],
        "wiki_image": city_info["image"],
        "timezone": timezone,
        "state": location["state"],
        "local_time": local_time.strftime("%I:%M %p"),
"country": location["country"],
"currency": country_info["currency"],
"timezone": country_info["timezone"],
"population": country_info["population"],
 })

@app.route("/tourist", methods=["POST"])
def tourist():

    data = request.json

    places = get_tourist_places(
        data["lat"],
        data["lon"]
    )

    return jsonify({
        "places": places
    })

@app.route("/news", methods=["POST"])
def news():
    data = request.json or {}

    city = data.get("city")

    if not city:
        return jsonify({"news": []})

    return jsonify({
        "news": get_news(city)
    })

def get_city_language(state, country):

    languages = {
        "Kerala": "Malayalam",
        "Tamil Nadu": "Tamil",
        "Karnataka": "Kannada",
        "Telangana": "Telugu",
        "Andhra Pradesh": "Telugu",
        "Maharashtra": "Marathi",
        "West Bengal": "Bengali",
        "Punjab": "Punjabi",
        "Gujarat": "Gujarati",
        "Rajasthan": "Hindi"
    }

    return languages.get(state, "Local Language")

def ai_place_intro(city, weather_desc, temp):
    city = city.lower()

    if city in ["paris", "london", "rome"]:
        base = "A world-famous cultural and historical city"
    elif city in ["tokyo", "seoul", "singapore"]:
        base = "A highly modern and technologically advanced city"
    elif city in ["new york", "dubai"]:
        base = "A fast-paced global business and tourism hub"
    else:
        base = "A diverse and interesting travel destination"

    if "rain" in weather_desc:
        weather_part = "currently experiencing rainy weather, ideal for indoor activities"
    elif temp > 30:
        weather_part = "hot climate, suitable for outdoor exploration"
    elif temp < 15:
        weather_part = "cold climate, good for cozy travel experiences"
    else:
        weather_part = "pleasant weather conditions for tourism"

    return f"{base} with {weather_part}."

def get_country_info(country):

    url = f"https://restcountries.com/v3.1/name/{country}"

    response = requests.get(url).json()

    
    if not isinstance(response, list):
        return {
        "language": "Unknown",
        "currency": "Unknown",
        "population": "Unknown",
        "timezone": "Unknown"
        }

    country_data = response[0]

    languages = ", ".join(country_data.get("languages", {}).values())

    currencies = country_data.get("currencies", {})

    currency = "Unknown"

    if currencies:
        currency = list(currencies.values())[0].get("name", "Unknown")

    population = country_data.get("population", "Unknown")

    timezone = country_data.get("timezones", ["Unknown"])[0]
    return {
        "language": languages,
        "currency": currency,
        "population": population,
         "timezone": timezone
    }

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)