from django.db import models

# Create your models here.

class Town(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    def __str__(self):
        return "Name: " + self.name + " Lat:" + str(self.latitude) + " Lon:" + str(self.longitude)

class BusCompany(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Bus(models.Model):
    company = models.ForeignKey(BusCompany, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    towns = models.ManyToManyField(Town)
    from_town = models.ForeignKey(Town, on_delete=models.CASCADE, related_name='from_town', default=1)
    to_town = models.ForeignKey(Town, on_delete=models.CASCADE, related_name='to_town', default=1)

    def __str__(self):
        trough_towns = ", ".join([town.__str__() for town in self.towns.all()])
        return f"{self.company.name} - {self.name} trough {trough_towns} towns"

class Route(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    towns = models.ManyToManyField(Town, through='RouteStop')

    def __str__(self):
        stops = self.routestop_set.order_by('position').select_related('town')
        return f"{self.bus.name} through " + ", ".join([stop.town.name for stop in stops])

class RouteStop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    town = models.ForeignKey(Town, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()

    class Meta:
        unique_together = ('route', 'town')
        ordering = ['position']

    def __str__(self):
        return f"{self.town.name} at position {self.position} on route {self.route.bus.name}"