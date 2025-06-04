import markdown
from bs4 import BeautifulSoup
from django.shortcuts import render, redirect
import re

# Create your views here.
from django.shortcuts import render
from .gemini_ai import ask_gemini
from .models import Route, Town, Bus, Ticket


def check_route(request):
    answer = None
    if request.method == "POST":
        from_town = request.POST.get("from_town")
        to_town = request.POST.get("to_town")

        all_busses = list(Bus.objects.filter(route__start_town__name=from_town, route__end_town__name=to_town).all())
        buses_info = "\n - ".join([bus.return_information() for bus in all_busses])
        if from_town and to_town:
            question = (
                f"Here are all the buses information and the towns they pass trough"
                f"1.{buses_info}"
                f"give me the shortest route in format"
                f"[id_of_bus, name_of_bus]"
                f"and tell me the distance compared to other buses"
                f"or another details"
                f"taking the latitude and longitude of the town and the road distance into considerance"
                f"but it must contain ONLY ONE int this format without as plain text [id_of_bus, name_of_bus] AND IT MUST BE IN THAT FORMAT"
                f"Taking into consideration the from_town ={from_town} and to_town ={to_town} as well."
            )
            return_busses = []
            answer = ask_gemini(question)
            html_content = markdown.markdown(answer)
            soup = BeautifulSoup(html_content, 'html.parser')
            html_content = str(soup)
            match = re.search(r'\[.*?\]', answer)
            if match:
                bus_registration, bus_name = match.group(0).replace("[", "").replace("]", "").split(",")
                return_busses = Bus.objects.filter(registration_number=bus_registration)
            else:
                return_busses = list(Bus.objects.all())
    if request.method == "GET":
        all_towns = Town.objects.all()
    return render(request, "busses.html", {'busses': return_busses, "answer": html_content})


def routes_list(request):
    routes = Route.objects.prefetch_related('routestop_set__town', 'bus')
    return render(request, 'routes.html', {'routes': routes})


def home(request):
    return render(request, 'home.html')


def busses(request):
    if request.user.is_authenticated:
        busses = Bus.objects.all()
        return render(request, 'busses.html', {'busses': busses})
    else:
        return redirect("home")


def tickets(request, user_id):
    if request.user.is_authenticated:
        if request.method == "POST":
            pass
        if request.method == "GET":
            found_tickets = Ticket.objects.filter(user_id=user_id)
            return render(request, 'tickets.html', {'tickets': found_tickets})
    else:
        return redirect("home")


def buy_ticket(request, bus_id):
    if request.user.is_authenticated:
        if request.method == "POST":
            bus = Bus.objects.get(id=bus_id)
            price = request.POST.get("discount_price")
            Ticket.objects.create(bus=bus, user=request.user, discounted_price=price)
            return redirect('tickets', user_id=request.user.id)
        if request.method == "GET":
            print(bus_id)
            bus = Bus.objects.get(id=bus_id)
            return render(request, 'buy_ticket.html', {'bus': bus})
    else:
        return redirect("home")


def delete_ticket(request, ticket_id):
    if request.user.is_authenticated:
        if request.method == "POST":
            ticket = Ticket.objects.get(id=ticket_id)
            if request.user == ticket.user:
                ticket.delete()
            return redirect('tickets', user_id=request.user.id)
    else:
        return redirect("home")
