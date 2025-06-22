import os

import requests
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

ORS_API_KEY = os.getenv("ORS_API_KEY")  # Replace with your actual key
ORS_BASE_URL = "https://api.openrouteservice.org/v2/directions/driving-car"

def get_road_distance_osm(lat1, lon1, lat2, lon2):
    headers = {
        'Authorization': ORS_API_KEY,
        'Content-Type': 'application/json'
    }

    payload = {
        "coordinates": [[lon1, lat1], [lon2, lat2]]
    }

    response = requests.post(ORS_BASE_URL, json=payload, headers=headers)

    if response.status_code == 200:
        summary = response.json()['routes'][0]['summary']
        distance_km = int(round(float(summary['distance']) / 1000, 2))
        duration_minutes = int(round(float(summary['duration']) / 60, 2))
        return round(distance_km, 2), round(duration_minutes, 2)
    else:
        print("Error from ORS:", response.status_code, response.text)
        return None, None
