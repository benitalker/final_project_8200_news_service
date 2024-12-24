import requests
from app.utils.config import GEO_API_KEY, GEOCODING_URL

def get_coordinates(location):
    params = {
        "q": location,
        "key": GEO_API_KEY
    }
    response = requests.get(GEOCODING_URL, params=params)
    response.raise_for_status()
    results = response.json().get('results', [])
    if results:
        geometry = results[0].get('geometry', {})
        return {
            "latitude": geometry.get("lat"),
            "longitude": geometry.get("lng"),
            "formatted_address": results[0].get("formatted", "")
        }
    return {}
