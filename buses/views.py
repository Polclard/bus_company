from collections import defaultdict
# Create your views here.
from collections import deque
from datetime import timedelta, datetime

from django.db import transaction
from django.db.models import Case, When, Count, Sum

from .models import Route, Ticket
from .models import Town, Bus


# def check_route(request):
#     from_town = to_town = None
#     answer = html_content = None
#     return_busses = []
#     all_towns = Town.objects.all()
#     shortest_bus_by_distance = None
#
#     if request.method == "POST":
#         from_town = request.POST.get("from_town")
#         to_town = request.POST.get("to_town")
#
#         if from_town and to_town:
#             from_town_obj = Town.objects.filter(name=from_town).first()
#             to_town_obj = Town.objects.filter(name=to_town).first()
#             print(f"from_town: {from_town}, to_town: {to_town}")
#             if from_town_obj and to_town_obj:
#                 qs1 = list(Bus.objects.filter(route__start_town=from_town_obj, route__end_town=to_town_obj))
#                 qs2 = list(Bus.objects.filter(route__towns=from_town_obj).filter(route__towns=to_town_obj))
#
#                 all_busses = (qs1 + qs2)
#                 return_busses = list(all_busses)
#                 print(all_busses)
#
#                 try:
#                     buses_info = "\n - ".join([bus.return_information() for bus in return_busses])
#
#                     question = (
#                         f"Here are all the buses information and the towns they pass through:\n"
#                         f"{buses_info}\n"
#                         f"Give me the shortest route in format [id_of_bus, name_of_bus]. "
#                         f"Tell me the distance compared to other buses, considering road distances between towns. "
#                         f"Your output MUST be only in the format [id_of_bus, name_of_bus]. "
#                         f"Start town: {from_town}, End town: {to_town}."
#                     )
#
#                     answer = ask_gemini(question)
#                     html_content = str(BeautifulSoup(markdown.markdown(answer), 'html.parser'))
#
#                     match = re.search(r'\[(.*?)\]', answer)
#                     if match:
#                         bus_registration, _ = match.group(1).split(",", 1)
#                         gemini_busses = Bus.objects.filter(registration_number=bus_registration.strip())
#                     else:
#                         gemini_busses = Bus.objects.none()
#
#                     # ORS Road Distance Calculation
#                     min_total_distance = float('inf')
#                     best_bus = None
#
#                     for bus in return_busses:
#                         route = bus.route
#                         full_towns = [route.start_town] + list(route.towns.all()) + [route.end_town]
#
#                         if from_town_obj in full_towns and to_town_obj in full_towns:
#                             from_index = full_towns.index(from_town_obj)
#                             to_index = full_towns.index(to_town_obj)
#
#                             if from_index < to_index:
#                                 sub_route = full_towns[from_index:to_index + 1]
#                                 total_distance = 0
#                                 valid = True
#
#                                 for i in range(len(sub_route) - 1):
#                                     lat1, lon1 = sub_route[i].latitude, sub_route[i].longitude
#                                     lat2, lon2 = sub_route[i + 1].latitude, sub_route[i + 1].longitude
#
#                                     dist, _ = get_road_distance_osm(lat1, lon1, lat2, lon2)
#
#                                     if dist is not None:
#                                         total_distance += dist
#                                     else:
#                                         valid = False
#                                         break
#
#                                 if valid and total_distance < min_total_distance:
#                                     min_total_distance = total_distance
#                                     best_bus = bus
#
#                     shortest_bus_by_distance = best_bus
#
#                     if gemini_busses.exists():
#                         # return_busses = list(gemini_busses)
#                         gemini_best_bus = list(gemini_busses)
#                         return_busses = Bus.objects.all()
#
#                 except Exception as e:
#                     print("Gemini/ORS error:", e)
#                     return_busses = []
#                     answer = None
#                     html_content = None
#                     shortest_bus_by_distance = None
#
#     return render(request, "busses.html", {
#         'busses': return_busses,
#         'answer': html_content,
#         'towns': all_towns,
#         'from_town': from_town,
#         'to_town': to_town,
#         'shortest_bus_by_distance': shortest_bus_by_distance,
#         'gemini_best_bus': gemini_best_bus[0],
#     })


def find_best_route(from_town_obj, to_town_obj, departure_datetime=None, desired_departure_time=None):
    bus_routes = {}
    bus_schedules = {}

    print(f"Searching routes for datetime: {departure_datetime}")

    # Use now if no departure_datetime (arrival time at current town)
    if departure_datetime is None:
        departure_datetime = datetime.now()

    # Base date for ticket filtering
    base_date = departure_datetime.date()

    # Fetch ticket counts grouped by bus and departure_date (only for base_date)
    tickets_qs = (
        Ticket.objects.filter(departure_date=base_date)
        .values('bus', 'departure_date')
        .annotate(count=Count('id'))
    )

    bus_tickets_per_date = defaultdict(int)  # key: (bus_id, departure_date), value: count
    for item in tickets_qs:
        bus_tickets_per_date[(item['bus'], item['departure_date'])] = item['count']

    # Build bus routes and schedules for all buses
    for bus in Bus.objects.select_related('route').all():
        route = bus.route
        ordered_town_ids = route.towns_order or []
        ordered_towns = list(
            Town.objects.filter(id__in=ordered_town_ids).order_by(
                Case(*[When(id=pk, then=pos) for pos, pk in enumerate(ordered_town_ids)])
            )
        )
        towns = [route.start_town] + ordered_towns + [route.end_town]
        bus_routes[bus] = towns

        num_segments = len(towns) - 1
        dep_time = datetime.combine(base_date, bus.departure_time)
        arr_time = datetime.combine(base_date, bus.arrival_time)

        # Handle overnight trips (arrival next day)
        if arr_time <= dep_time:
            arr_time += timedelta(days=1)

        total_duration = (arr_time - dep_time).total_seconds()
        segment_duration = total_duration / num_segments

        estimated_times = []
        for i in range(len(towns)):
            est_time = dep_time + timedelta(seconds=segment_duration * i)
            estimated_times.append(est_time)
        bus_schedules[bus] = dict(zip(towns, estimated_times))

    instructions = ""

    # === DIRECT ROUTE: find bus with closest departure time (before or after) ===
    candidate_buses = []

    for bus, towns in bus_routes.items():
        if from_town_obj in towns and to_town_obj in towns:
            from_idx = towns.index(from_town_obj)
            to_idx = towns.index(to_town_obj)
            if from_idx < to_idx:
                dep_time_from = bus_schedules[bus][from_town_obj]
                bus_departure_date = dep_time_from.date()

                seats_taken = bus_tickets_per_date.get((bus.id, bus_departure_date), 0)
                if seats_taken >= bus.number_of_seats:
                    continue  # Skip full bus

                # Calculate absolute time difference in seconds
                time_diff = abs((dep_time_from - departure_datetime).total_seconds())
                candidate_buses.append((time_diff, bus, dep_time_from))

    if candidate_buses:
        candidate_buses.sort(key=lambda x: x[0])
        best_time_diff, best_bus, best_dep_time = candidate_buses[0]

        instructions += (f"Take bus '{best_bus.name}' from {from_town_obj.name} at "
                         f"{best_dep_time.strftime('%H:%M')} straight to {to_town_obj.name} arriving at "
                         f"{bus_schedules[best_bus][to_town_obj].strftime('%H:%M')}\n")

        # Return the list of buses and the instructions string
        return [best_bus], instructions

    # Helper function to build visited state key with arrival time rounded to minutes
    def get_state_key(town_id, buses_taken, arrival_time):
        rounded_time = arrival_time.replace(second=0, microsecond=0)
        bus_ids = tuple(bus.id for bus in buses_taken)
        return (town_id, bus_ids, rounded_time)

    # === BFS for indirect routes ===
    queue = deque([(from_town_obj, [], set(), departure_datetime)])
    visited_states = set()

    while queue:
        current_town, buses_taken, visited_buses, arrival_time_at_current = queue.popleft()

        if current_town == to_town_obj:
            if not buses_taken:
                instructions += f"You are already at {to_town_obj.name}\n"
            else:
                board_town = from_town_obj

                for i, bus in enumerate(buses_taken):
                    towns = bus_routes[bus]
                    board_idx = towns.index(board_town)

                    if i == len(buses_taken) - 1:
                        alight_town = to_town_obj
                    else:
                        next_bus = buses_taken[i + 1]
                        next_towns = bus_routes[next_bus]
                        after_board = towns[board_idx + 1:]
                        alight_town = None
                        for town in after_board:
                            if town in next_towns:
                                alight_town = town
                                break
                        if alight_town is None:
                            alight_town = next_towns[0]

                    dep_time_str = bus_schedules[bus][board_town].strftime('%H:%M')
                    arr_time_str = bus_schedules[bus][alight_town].strftime('%H:%M')

                    instructions += f"Take bus '{bus.name}' from {board_town.name} at {dep_time_str} to {alight_town.name} arriving at {arr_time_str}\n"

                    if i < len(buses_taken) - 1:
                        layover = (bus_schedules[buses_taken[i + 1]][alight_town] - bus_schedules[bus][
                            alight_town]).total_seconds()
                        layover_minutes = int(layover // 60)
                        instructions += f"Change at {alight_town.name}, layover time: {layover_minutes} minutes\n"

                    board_town = alight_town

            instructions += f"Arrive at {to_town_obj.name}\n"

            return buses_taken, instructions

        for bus, towns in bus_routes.items():
            if bus in visited_buses:
                continue

            if current_town in towns:
                idx = towns.index(current_town)
                for next_idx in range(idx + 1, len(towns)):
                    next_town = towns[next_idx]

                    est_arrival_current = bus_schedules[bus][current_town]
                    est_arrival_next = bus_schedules[bus][next_town]

                    bus_departure_date = est_arrival_current.date()
                    seats_taken = bus_tickets_per_date.get((bus.id, bus_departure_date), 0)
                    if seats_taken >= bus.number_of_seats:
                        continue  # Bus full on that departure date, skip

                    if not buses_taken:
                        can_take = True
                    else:
                        waiting_time = (est_arrival_current - arrival_time_at_current).total_seconds()
                        can_take = waiting_time >= 3600  # 1 hour layover

                    if can_take:
                        new_buses_taken = buses_taken
                        if not buses_taken or buses_taken[-1] != bus:
                            new_buses_taken = buses_taken + [bus]

                        state_key = get_state_key(next_town.id, new_buses_taken, est_arrival_next)
                        if state_key not in visited_states:
                            visited_states.add(state_key)
                            queue.append((next_town, new_buses_taken, visited_buses | {bus}, est_arrival_next))

    instructions += "No connection found between these towns.\n"
    return [], instructions


def check_route(request):
    from_town = to_town = None
    departure_time_str = None
    departure_date_str = None
    all_towns = Town.objects.all()
    route_instructions = ""
    return_busses = []

    if request.method == "POST":
        from_town = request.POST.get("from_town")
        to_town = request.POST.get("to_town")
        departure_date_str = request.POST.get("date")
        departure_time_str = request.POST.get("departure_time")

        if from_town and to_town:
            from_town_obj = Town.objects.filter(name=from_town).first()
            to_town_obj = Town.objects.filter(name=to_town).first()
            if from_town_obj and to_town_obj:
                if departure_date_str:
                    try:
                        parsed_date = datetime.strptime(departure_date_str, "%Y-%m-%d").date()
                    except ValueError:
                        parsed_date = datetime.today().date()
                else:
                    parsed_date = datetime.today().date()

                if departure_time_str:
                    try:
                        parsed_time = datetime.strptime(departure_time_str, "%H:%M").time()
                    except ValueError:
                        parsed_time = datetime.min.time()
                else:
                    parsed_time = datetime.min.time()

                departure_datetime = datetime.combine(parsed_date, parsed_time)

                # The find_best_route function should be modified to return the instructions string
                # along with the list of buses.
                return_busses, route_instructions = find_best_route(
                    from_town_obj,
                    to_town_obj,
                    departure_datetime=departure_datetime
                )

    return render(request, "check_route.html", {
        'towns': all_towns,
        'from_town': from_town or '',
        'to_town': to_town or '',
        'date': departure_date_str or '',
        'departure_time': departure_time_str or '',
        'route_instructions': route_instructions,
        'busses': return_busses,  # Optionally pass the buses to display them as cards
    })


def routes_list(request):
    routes = Route.objects.prefetch_related('routestop_set__town', 'bus')
    return render(request, 'routes.html', {'routes': routes})


def home(request):
    return render(request, 'home.html')


def busses(request):
    if request.user.is_authenticated:
        busses = Bus.objects.all()
        all_towns = Town.objects.all()  # Fetch all towns from the database
        return render(request, 'busses.html', {
            'busses': busses,
            'towns': all_towns  # Pass the towns list to the template
        })
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


def buy_all_tickets(request):
    """
    This view collects the bus IDs and departure date from the form
    and redirects the user to the confirmation page.
    """
    if not request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        bus_ids = request.POST.getlist("bus_ids")
        departure_date = request.POST.get("departure_date")

        if not bus_ids:
            messages.error(request, "No buses were selected to purchase.")
            return redirect("check_route")

        # Get the URL string first, then add the query parameters.
        # This fixes the "Page not found" error.
        base_url = redirect('confirm_all_tickets').url
        query_params = '&'.join([f'bus_ids={id}' for id in bus_ids])
        return redirect(f"{base_url}?{query_params}&departure_date={departure_date}")

    return redirect("home")


def confirm_all_tickets(request):
    """
    This view handles displaying the confirmation page (GET) and
    processing the final purchase (POST).
    """
    if not request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        bus_ids = request.POST.getlist("bus_ids")
        departure_date_str = request.POST.get("departure_date")
        departure_date = parse_date(departure_date_str)

        try:
            with transaction.atomic():
                total_price = 0
                for bus_id in bus_ids:
                    bus = get_object_or_404(Bus, id=bus_id)

                    occupied_seats = Ticket.objects.filter(bus=bus, departure_date=departure_date).count()
                    if occupied_seats >= bus.number_of_seats:
                        messages.warning(request, f"Bus '{bus.name}' is full. Ticket for this bus not purchased.")
                        continue

                    Ticket.objects.create(
                        bus=bus,
                        user=request.user,
                        discounted_price=bus.price,
                        departure_date=departure_date
                    )
                    total_price += bus.price

            messages.success(request, f"All tickets purchased successfully for a total of ${total_price:.2f}!")
            return redirect('tickets', user_id=request.user.id)

        except Exception as e:
            messages.error(request, f"An error occurred while purchasing tickets: {e}")
            return redirect("check_route")

    # Handle GET request (display confirmation page)
    bus_ids = request.GET.getlist("bus_ids")
    departure_date_str = request.GET.get("departure_date")

    if not bus_ids or not departure_date_str:
        messages.error(request, "Invalid request. Please search for a route again.")
        return redirect("check_route")

    busses = Bus.objects.filter(id__in=bus_ids)

    # Calculate the total price
    total_price = busses.aggregate(total=Sum('price'))['total'] or 0

    context = {
        'busses': busses,
        'departure_date': departure_date_str,
        'total_price': total_price,
    }
    return render(request, 'confirm_all_tickets.html', context)
