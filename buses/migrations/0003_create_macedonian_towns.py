from django.db import migrations

def create_macedonian_towns(apps, schema_editor):
    Town = apps.get_model("buses", "Town")

    towns_data = [
        ("Skopje", 41.9981, 21.4254),
        ("Bitola", 41.0316, 21.3342),
        ("Ohrid", 41.1231, 20.8016),
        ("Prilep", 41.3451, 21.5550),
        ("Tetovo", 42.0095, 20.9716),
        ("Gostivar", 41.8003, 20.9144),
        ("Struga", 41.1778, 20.6783),
        ("Kumanovo", 42.1322, 21.7144),
        ("Veles", 41.7156, 21.7756),
        ("Kavadarci", 41.4331, 22.0114),
        ("Strumica", 41.4378, 22.6427),
        ("Gevgelija", 41.1414, 22.5011),
        ("Kochani", 41.9164, 22.4125),
        ("Shtip", 41.7458, 22.1956),
        ("Kichevo", 41.5120, 20.9584),
        ("Negotino", 41.4864, 22.0886),
        ("Debar", 41.5244, 20.5242),
        ("Delchevo", 41.9670, 22.7695),
        ("Radovish", 41.6383, 22.4650),
        ("Berovo", 41.7101, 22.8516),
        ("Kratovo", 42.0809, 22.1739),
        ("Krushevo", 41.3672, 21.2484),
        ("Resen", 41.0883, 21.0125),
        ("Vinica", 41.8828, 22.5092),
        ("Bogdanci", 41.2039, 22.5761),
        ("Demir Kapija", 41.4061, 22.2442),
        ("Demir Hisar", 41.2208, 21.2025),
    ]

    for name, lat, lon in towns_data:
        if not Town.objects.filter(name=name).exists():
            Town.objects.create(name=name, latitude=lat, longitude=lon)

class Migration(migrations.Migration):

    dependencies = [
        ('buses', '0002_bus_description_bus_image_alter_bus_arrival_time_and_more'),  # Adjust if your initial migration is different
    ]

    operations = [
        migrations.RunPython(create_macedonian_towns),
    ]
