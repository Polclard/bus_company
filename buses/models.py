from django.db import models

# Create your models here.

class BusCompany(models.Model):
    name = models.CharField(max_length=255)
    headquarters = models.CharField(max_length=255)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Bus(models.Model):
    company = models.ForeignKey(BusCompany, on_delete=models.CASCADE)
    bus_number = models.CharField(max_length=20, unique=True)
    capacity = models.PositiveIntegerField()
    license_plate_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.bus_number} - {self.company.name}"

class Town(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Route(models.Model):
    name = models.CharField(max_length=255)
    towns = models.ManyToManyField(Town, related_name="routes")

    def __str__(self):
        return self.name

class Trip(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Trip {self.bus.bus_number} on {self.route}"