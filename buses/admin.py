from django.contrib import admin

from buses.models import BusCompany, Bus, Route, Trip

# Register your models here.
admin.site.register(BusCompany)
admin.site.register(Bus)
admin.site.register(Route)
admin.site.register(Trip)