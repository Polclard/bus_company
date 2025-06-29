import random

from django.db import migrations, models

def populate_number_of_seats_for_busses(apps, schema_editor):
    Bus = apps.get_model('buses', 'Bus')

    for bus in Bus.objects.all():
        bus.number_of_seats = random.randint(10, 40)
        bus.save()

class Migration(migrations.Migration):

    dependencies = [
        ("buses", "0009_bus_number_of_seats_ticket_departure_date"),
    ]

    operations = [
        migrations.RunPython(populate_number_of_seats_for_busses),
    ]
