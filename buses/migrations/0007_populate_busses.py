from django.db import migrations
import random
import datetime
from datetime import timedelta

def create_buses_for_routes(apps, schema_editor):
    Bus = apps.get_model('buses', 'Bus')
    Route = apps.get_model('buses', 'Route')
    BusCompany = apps.get_model('buses', 'BusCompany')

    companies = list(BusCompany.objects.all())
    if not companies:
        return

    for route in Route.objects.all():
        company = random.choice(companies)

        # Fixed number of buses per route
        num_buses = 5

        earliest_departure = datetime.time(hour=6, minute=0)
        departure_times = []

        for i in range(num_buses):
            if i == 0:
                departure = earliest_departure
            else:
                prev_dep = departure_times[-1]
                prev_dep_dt = datetime.datetime.combine(datetime.date.today(), prev_dep)
                new_dep_dt = prev_dep_dt + timedelta(hours=3)
                departure = new_dep_dt.time()

            # Random duration between 3 to 5 hours
            duration_hours = random.randint(3, 5)
            dep_dt = datetime.datetime.combine(datetime.date.today(), departure)
            arr_dt = dep_dt + timedelta(hours=duration_hours)
            arrival = arr_dt.time()

            departure_times.append(departure)

            reg_number = f"MK{random.randint(1000, 9999)}"
            bus_name = f"Express {route.start_town.name} to {route.end_town.name} #{i + 1}"

            Bus.objects.create(
                name=bus_name,
                description=f"Bus route from {route.start_town.name} to {route.end_town.name}",
                registration_number=reg_number,
                company=company,
                route=route,
                departure_time=departure,
                arrival_time=arrival,
                price=15.00,
            )

class Migration(migrations.Migration):

    dependencies = [
        ('buses', '0006_populate_routes_part_two'),
    ]

    operations = [
        migrations.RunPython(create_buses_for_routes),
    ]
