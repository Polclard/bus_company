from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .gemini_ai import ask_gemini
from .models import RouteStop, Route, Town, Bus


def check_route(request):
    answer = None

    if request.method == "POST":
        from_town = request.POST.get("from_town")
        to_town = request.POST.get("to_town")
        through_town = request.POST.get("through_town")

        all_busses = list(Bus.objects.filter(from_town__name=from_town, to_town__name=to_town))
        if from_town and to_town and through_town:
            # question = (
            #     f"Does a bus from {from_town} to {to_town} pass through {through_town} "
            #     "in Macedonia? Answer like you're helping a travel planner. Taking into account the "
            #     "following information about routes:" +
            #     f"{Route.objects.all()}"
            # )
            question =(
                f"Given the buses information and the towns they pass trough {all_busses.__str__()}"
                f" give me the shortest route in format"
                f" (If you want to go from from_town to to_town the shortest route is [and here put the buss that goes"
                f" trough the shortest route and all of the towns it goes trough])"
                f" and only the town names without the location"
                f" or another details"
                f"Taking into consideration the from_town ={from_town} and to_town ={to_town}"
            )
            answer = ask_gemini(question)

    if request.method == "GET":
        all_towns = Town.objects.all()
    return render(request, "check_route.html", {"answer": answer})


def routes_list(request):
    routes = Route.objects.prefetch_related('routestop_set__town', 'bus')
    return render(request, 'routes.html', {'routes': routes})


def home(request):

    return render(request, 'home.html', {'routes': routes})