import datetime

from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Town(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class BusCompany(models.Model):
    name = models.CharField(max_length=100)
    origin_town = models.ForeignKey(Town, on_delete=models.CASCADE, related_name='companies')
    registration_number = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Route(models.Model):
    start_town = models.ForeignKey(Town, on_delete=models.CASCADE, related_name='routes_starting')
    end_town = models.ForeignKey(Town, on_delete=models.CASCADE, related_name='routes_ending')
    towns = models.ManyToManyField(Town, related_name='routes_passing_through')

    def __str__(self):
        towns = ', '.join([f"{town.name} - lat:{town.latitude} - lon:{town.longitude}" for town in self.towns.all()])
        return f"{self.start_town}, trough-> | {towns} | -> {self.end_town}"


class Bus(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, default='')
    registration_number = models.CharField(max_length=50)
    company = models.ForeignKey(BusCompany, on_delete=models.CASCADE, related_name='company_buses')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='route_buses')
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    number_of_seats = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.name} - ({self.registration_number})"

    def return_information(self):
        return (f"Bus Info: {self.name} - ({self.registration_number} - "
                f"{self.departure_time} - {self.arrival_time} - "
                f"{self.price} - {self.description} - {self.company.name})"
                f"Route Info {self.route.__str__()})")


class Ticket(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='bus_tickets')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_tickets')
    discounted_price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    departure_date= models.DateField(default=datetime.date.today)

    def __str__(self):
        return f"Ticket for {self.user} on {self.bus}"

class TownDistance(models.Model):
    from_town = models.ForeignKey(Town, on_delete=models.CASCADE, related_name='distances_from')
    to_town = models.ForeignKey(Town, on_delete=models.CASCADE, related_name='distances_to')
    distance_km = models.FloatField()  # Road distance in kilometers
    duration_minutes = models.IntegerField()  # Optional: driving duration
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('from_town', 'to_town')

    def __str__(self):
        return f"{self.from_town.name} → {self.to_town.name}: {self.distance_km} km"
