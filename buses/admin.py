from django.contrib import admin

from buses.models import Town, Route, BusCompany, Bus, Ticket, TownDistance

# Register your models here.

admin.site.register(Town)
admin.site.register(BusCompany)
admin.site.register(Bus)
admin.site.register(Route)
admin.site.register(Ticket)
admin.site.register(TownDistance)
