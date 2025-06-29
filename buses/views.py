import re
from datetime import datetime

import markdown
from bs4 import BeautifulSoup
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.dateparse import parse_date

from .gemini_ai import ask_gemini
# Create your views here.
from .models import Route, Ticket
from .models import Town, Bus, TownDistance
from .utils_funcs.route_distance import get_road_distance_osm


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
            print(f"from_town: {from_town}, to_town: {to_town}")
            if from_town_obj and to_town_obj:
                qs1 = list(Bus.objects.filter(route__start_town=from_town_obj, route__end_town=to_town_obj))
                qs2 = list(Bus.objects.filter(route__towns=from_town_obj).filter(route__towns=to_town_obj))

                all_busses = (qs1 + qs2)
                return_busses = list(all_busses)
                print(all_busses)

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

                    # ORS Road Distance Calculation
                    min_total_distance = float('inf')
                    best_bus = None

                    for bus in return_busses:
                        route = bus.route
                        full_towns = [route.start_town] + list(route.towns.all()) + [route.end_town]

                        if from_town_obj in full_towns and to_town_obj in full_towns:
                            from_index = full_towns.index(from_town_obj)
                            to_index = full_towns.index(to_town_obj)

                            if from_index < to_index:
                                sub_route = full_towns[from_index:to_index + 1]
                                total_distance = 0
                                valid = True

                                for i in range(len(sub_route) - 1):
                                    lat1, lon1 = sub_route[i].latitude, sub_route[i].longitude
                                    lat2, lon2 = sub_route[i + 1].latitude, sub_route[i + 1].longitude

                                    dist, _ = get_road_distance_osm(lat1, lon1, lat2, lon2)

                                    if dist is not None:
                                        total_distance += dist
                                    else:
                                        valid = False
                                        break

                                if valid and total_distance < min_total_distance:
                                    min_total_distance = total_distance
                                    best_bus = bus

                    shortest_bus_by_distance = best_bus

                    if gemini_busses.exists():
                        # return_busses = list(gemini_busses)
                        gemini_best_bus = list(gemini_busses)
                        return_busses = Bus.objects.all()

                except Exception as e:
                    print("Gemini/ORS error:", e)
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
        'shortest_bus_by_distance': shortest_bus_by_distance,
        'gemini_best_bus': gemini_best_bus[0],
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


from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date
from django.shortcuts import render, redirect, get_object_or_404

def buy_ticket(request, bus_id):
    if not request.user.is_authenticated:
        return redirect("home")

    bus = get_object_or_404(Bus, id=bus_id)

    if request.method == "POST":
        selected_date = request.POST.get("departure_date")
        price = request.POST.get("discount_price")
        departure_date = parse_date(selected_date)

        try:
            ticket = Ticket(
                bus=bus,
                user=request.user,
                discounted_price=price,
                departure_date=departure_date
            )
            ticket.full_clean()
            ticket.save()
            messages.success(request, "Ticket purchased successfully!")
            return redirect('tickets', user_id=request.user.id)

        except ValidationError as e:
            messages.error(request, ' '.join(e.messages))

        # Fall through to re-render the form with error message
        occupied_seats = Ticket.objects.filter(bus=bus, departure_date=departure_date).count()
        free_seats = bus.number_of_seats - occupied_seats

        return render(request, 'buy_ticket.html', {
            'bus': bus,
            'number_of_free_seats': free_seats,
            'selected_date': selected_date
        })


    else:

        selected_date = request.GET.get("departure_date")

        if selected_date:

            departure_date = parse_date(selected_date)

        else:

            import datetime

            departure_date = datetime.date.today()

            selected_date = departure_date.strftime('%Y-%m-%d')  # for rendering in the input

        occupied_seats = Ticket.objects.filter(bus=bus, departure_date=departure_date).count()

        free_seats = bus.number_of_seats - occupied_seats

        return render(request, 'buy_ticket.html', {

            'bus': bus,

            'number_of_free_seats': free_seats,

            'selected_date': selected_date

        })


def delete_ticket(request, ticket_id):
    if request.user.is_authenticated:
        if request.method == "POST":
            ticket = Ticket.objects.get(id=ticket_id)
            if request.user == ticket.user:
                ticket.delete()
            return redirect('tickets', user_id=request.user.id)
    else:
        return redirect("home")
