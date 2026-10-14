import geopy
import requests

geolocator = geopy.geocoders.Nominatim(
    user_agent="solar_project"
)


def city_to_coordinates(city, verbose=False):
    try:
        response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=10,
        )
        response.raise_for_status()
        results = response.json().get("results")
    except requests.RequestException:
        return None

    if not results:
        return None

    return results[0]["latitude"], results[0]["longitude"]



def coordinates_to_city(latitude, longitude):
    try:
        response = requests.get(
            "https://api.bigdatacloud.net/data/reverse-geocode-client",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "localityLanguage": "en",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return None

    name = data.get("city") or data.get("locality") or data.get("principalSubdivision")
    country = data.get("countryName")

    if not name:
        return country or None

    return f"{name}, {country}" if country else name
