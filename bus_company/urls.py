"""
URL configuration for bus_company project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from bus_company import settings
from buses import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),  # new
    path("accounts/", include("django.contrib.auth.urls")),
    path("check-route/", views.check_route, name="check_route"),
    path('routes/', views.routes_list, name='routes_list'),
    path('busses/', views.busses, name='busses'),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("buy_ticket/<int:bus_id>/", views.buy_ticket, name="buy_ticket"),
    path("tickets/<int:user_id>/", views.tickets, name="tickets"),
    path("delete_ticket/<int:ticket_id>/", views.delete_ticket, name="delete_ticket"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
