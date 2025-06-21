from django.db import migrations
import requests
import os
import time
from dotenv import load_dotenv

def fetch_and_save_distances(apps, schema_editor):
    Town = apps.get_model('buses', 'Town')
    TownDistance = apps.get_model('buses', 'TownDistance')


    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=env_path)

    ORS_API_KEY = os.getenv("ORS_API_KEY")
    if not ORS_API_KEY:
        print("❌ ORS_API_KEY is not set in environment variables.")
        return

    towns = list(Town.objects.all())
    total_pairs = len(towns) * (len(towns) - 1)

    headers = {
        'Authorization': ORS_API_KEY,
        'Content-Type': 'application/json'
    }

    for i, from_town in enumerate(towns):
        for j, to_town in enumerate(towns):
            if from_town.id == to_town.id:
                continue

            # Skip if already exists
            if TownDistance.objects.filter(from_town=from_town, to_town=to_town).exists():
                continue

            url = "https://api.openrouteservice.org/v2/directions/driving-car"
            payload = {
                "coordinates": [
                    [from_town.longitude, from_town.latitude],
                    [to_town.longitude, to_town.latitude]
                ]
            }

            try:
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    summary = response.json()['routes'][0]['summary']
                    distance_km = int(round(float(summary['distance']) / 1000, 2))
                    duration_min = int(round(float(summary['duration']) / 60, 2))
                    TownDistance.objects.create(
                        from_town=from_town,
                        to_town=to_town,
                        distance_km=distance_km,
                        duration_minutes=duration_min
                    )
                    print(f"✅ {from_town.name} → {to_town.name}: {distance_km} km, {duration_min} min")
                else:
                    print(f"❌ ORS error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"❌ Exception: {e}")

            time.sleep(2)

class Migration(migrations.Migration):

    dependencies = [
        ('buses', '0008_towndistance'),  # adjust to your last real migration
    ]

    operations = [
        migrations.RunPython(fetch_and_save_distances),
    ]
