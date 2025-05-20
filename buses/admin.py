from django.contrib import admin

from buses.models import Town, RouteStop, Route, BusCompany, Bus

# Register your models here.

admin.site.register(Town)
admin.site.register(BusCompany)
admin.site.register(Bus)
admin.site.register(Route)
admin.site.register(RouteStop)
