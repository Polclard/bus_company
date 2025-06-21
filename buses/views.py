import re

import markdown
from bs4 import BeautifulSoup
from django.shortcuts import redirect
from django.shortcuts import render

from .gemini_ai import ask_gemini
# Create your views here.
from .models import Route, Ticket
from .models import Town, Bus, TownDistance


def check_route(request):
    from_town = to_town = None
    answer = html_content = None
    return_busses = []
    all_towns = Town.objects.all()
    shortest_bus_by_distance = None

    if request.method == "POST":
        from_town = request.POST.get("from_town")
        to_town = request.POST.get("to_town")

        if from_town and to_town:
            from_town_obj = Town.objects.filter(name=from_town).first()
            to_town_obj = Town.objects.filter(name=to_town).first()
            print(from_town_obj, to_town_obj)
            if from_town_obj and to_town_obj:
                all_busses = (Bus.objects.filter(
                    route__start_town=from_town_obj, route__end_town=to_town_obj
                ) or
                Bus.objects.filter(
                    route__towns=from_town_obj
                ).filter(
                    route__towns=to_town_obj
                ).distinct())

                return_busses = list(all_busses)
                print(return_busses)
                if return_busses:
                    try:
                        buses_info = "\n - ".join([bus.return_information() for bus in return_busses])

                        question = (
                            f"Here are all the buses information and the towns they pass through:\n"
                            f"{buses_info}\n"
                            f"Give me the shortest route in format [id_of_bus, name_of_bus]. "
                            f"Tell me the distance compared to other buses, considering road distances between towns. "
                            f"Your output MUST be only in the format [id_of_bus, name_of_bus]. "
                            f"Start town: {from_town}, End town: {to_town}."
                        )

                        answer = ask_gemini(question)
                        html_content = str(BeautifulSoup(markdown.markdown(answer), 'html.parser'))

                        match = re.search(r'\[(.*?)\]', answer)
                        if match:
                            bus_registration, _ = match.group(1).split(",", 1)
                            gemini_busses = Bus.objects.filter(registration_number=bus_registration.strip())
                        else:
                            gemini_busses = Bus.objects.none()

                        min_total_distance = float('inf')
                        best_bus = None

                        for bus in return_busses:
                            towns = list(bus.route.towns.all())
                            if from_town_obj in towns and to_town_obj in towns:
                                from_index = towns.index(from_town_obj)
                                to_index = towns.index(to_town_obj)

                                if from_index < to_index:
                                    route_slice = towns[from_index:to_index + 1]
                                    total_distance = 0
                                    valid = True

                                    for i in range(len(route_slice) - 1):
                                        try:
                                            td = TownDistance.objects.get(
                                                from_town=route_slice[i],
                                                to_town=route_slice[i + 1]
                                            )
                                            total_distance += td.distance_km
                                        except TownDistance.DoesNotExist:
                                            valid = False
                                            break

                                    if valid and total_distance < min_total_distance:
                                        min_total_distance = total_distance
                                        best_bus = bus
                        print(f"Best bus: {best_bus}")
                        shortest_bus_by_distance = best_bus

                        if gemini_busses.exists():
                            return_busses = list(gemini_busses)

                    except Exception:
                        return_busses = []
                        answer = None
                        html_content = None
                        shortest_bus_by_distance = None

    return render(request, "busses.html", {
        'busses': return_busses,
        'answer': html_content,
        'towns': all_towns,
        'from_town': from_town,
        'to_town': to_town,
        'shortest_bus_by_distance': shortest_bus_by_distance
    })



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
