from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from route import models


def route_filter(request):
    if request.method == 'GET':
        country_list = set()
        country_objs = models.Places.objects.all()
        for itm in range(len(country_objs)):
            country_list.add(country_objs[itm].name_country)
        return render(request, 'route_filter.html', {'country_list': country_list})

    if request.method == 'POST':
        cursor = connection.cursor()
        query_filter = []

        if request.POST.get('route_type') != 'ALL':
            query_filter.append(f"route_type='{request.POST.get('route_type')}'")
        if request.POST.get('country') != 'ALL':
            query_filter.append(f"country='{request.POST.get('country')}'")
        if request.POST.get('location') != '':
            query_filter.append(f"location='{request.POST.get('location')}'")

        if query_filter:
            filter_str = f" WHERE {' and '.join(query_filter)}"
        else:
            filter_str = ""

        sql_query = """SELECT   route_route.country,
                                route_route.description,
                                route_route.duration,
                                route_route.stopping_point,
                                route_route.route_type,
                                start_point.name,
                                end_point.name
                        FROM route_route
                            JOIN route_places as start_point
                                ON start_point.id == route_route.starting_point
                            JOIN route_places as end_point
                                ON end_point.id == route_route.destination"""

        cursor.execute(sql_query + filter_str)

        result_query = cursor.fetchall()

        if result_query:
            list_route = [{"Country": i[0],
                           "Description": i[1],
                           "Duration route": i[2],
                           "Stopping point": i[3],
                           "Route type": i[4],
                           "Start point": i[5],
                           "End point": i[6]} for i in result_query]

            return HttpResponse(list_route)
        else:
            return HttpResponse('Routes not found')


def route_info(request):
    if request.method == 'GET':
        return render(request, 'info_route.html')

    if request.method == 'POST':
        actual_date = datetime.now().strftime('%Y-%m-%d')
        cursor = connection.cursor()

        sql_query_route = f"""SELECT  route_route.country,
                                route_route.description,
                                route_route.duration,
                                route_route.stopping_point,
                                route_route.route_type,
                                start_point.name,
                                end_point.name
                        FROM route_route
                            JOIN route_places as start_point
                                ON start_point.id == route_route.starting_point
                            JOIN route_places as end_point
                                ON end_point.id == route_route.destination
                            WHERE route_route.id == '{request.POST.get('id_route')}'"""

        cursor.execute(sql_query_route)
        result_query_route = cursor.fetchall()
        if result_query_route:
            select_route = [{"Country": i[0],
                             "Description": i[1],
                             "Duration": i[2],
                             "Stopping point": i[3],
                             "Route type": i[4],
                             "Start point": i[5],
                             "End point": i[6]} for i in result_query_route]

            sql_query_event = f"""SELECT event.id,
                                         event.start_date,
                                         event.price
                                  FROM route_event as event
                                      JOIN route_route as route
                                        ON route.id == event.id_route
                                  WHERE route.id == '{request.POST.get('id_route')}' 
                                        and event.start_date >= '{actual_date}'"""

            cursor.execute(sql_query_event)
            result_query_route_event = cursor.fetchall()
            if result_query_route_event:
                travel_events = [{'ID Event': i[0],
                                  'Date start event': i[1],
                                  'Price event': i[2]} for i in result_query_route_event]

                return HttpResponse([select_route, travel_events, '<br><a href="info_event" >SELECT  EVENT</a>',
                                                                  '<br><a href="add_event" >ADD NEW EVENT</a>'])

            else:
                return HttpResponse([select_route, '<br><a href="add_event" >ADD NEW EVENT</a>'])

        else:
            return HttpResponse('Route not found')


def route_add(request):
    if request.user.has_perm('route.add_route'):
        if request.method == 'GET':
            places_list = []
            country_list = set()
            place_objs = models.Places.objects.all()
            for itm in range(len(place_objs)):
                places_list.append(place_objs[itm].name)
                country_list.add(place_objs[itm].name_country)
            return render(request, 'add_route.html', {'places_list': places_list,
                                                      'country_list': country_list,
                                                      'limit_duration': range(1, 11)})

        if request.method == 'POST':
            starting_point = request.POST.get('starting_point')
            destination = request.POST.get('destination')
            country = request.POST.get('country')
            location = request.POST.get('location')
            description = request.POST.get('description')
            duration = request.POST.get('duration')
            route_type = request.POST.get('route_type')

            start_obj = models.Places.objects.get(name=starting_point)
            destination_obj = models.Places.objects.get(name=destination)
            new_route = models.Route(starting_point=start_obj.id,
                                     stopping_point={},
                                     destination=destination_obj.id,
                                     country=country,
                                     location=location,
                                     description=description,
                                     duration=duration,
                                     route_type=route_type)
            new_route.save()
            return HttpResponse('Creating a route')
    else:
        return HttpResponse('Not allowed to add route')


def route_reviews(request):
    if request.method == 'GET':
        return render(request, 'route_review.html')

    if request.method == 'POST':
        result = models.Review.objects.all().filter(route_id=request.POST.get('id_route'))
        if result:
            return HttpResponse([{'route_id': i.route_id,
                                  'review_text': i.review_text,
                                  'review_rate': i.review_rate} for i in result])
        else:
            return HttpResponse('Not found reviews')


def route_add_event(request):
    if request.user.has_perm('route.add_event'):
        if request.method == 'GET':
            return render(request, 'add_event.html')

        if request.method == 'POST':
            route_id = request.POST.get('id_route')
            start_date = request.POST.get('start_date')
            price = request.POST.get('price')

            new_event = models.Event(id_route=route_id,
                                     start_date=start_date,
                                     price=price,
                                     event_admin=1,
                                     approved_users={},
                                     pending_users={})
            new_event.save()
            return HttpResponse('Event added')
    else:
        return HttpResponse('Not allowed to add event')


def event_info(request):
    if request.method == 'GET':
        return render(request, 'info_event.html')

    if request.method == 'POST':
        cursor = connection.cursor()
        sql_query = f"""SELECT  event.id,
                               event.start_date,
                               event.price,
                               route.country,
                               route.location,
                               route.stopping_point,
                               place.name_country,
                               place.name,
                               route.duration,
                               route.route_type

                        FROM route_event as event
                            JOIN route_route as route
                                ON event.id_route == route.id
                            JOIN route_places as place
                                ON route.destination == place.id
                            WHERE event.id == '{request.POST.get('id_event')}'"""

        cursor.execute(sql_query)
        result = cursor.fetchall()
        if result:
            list_event = [{'ID event': i[0],
                           'Date start event': i[1],
                           'Price': i[2],
                           'Country start': i[3],
                           'Start point': i[4],
                           'Stopping point': i[5],
                           'Country end': i[6],
                           'End point': i[7],
                           'Duration event': i[8],
                           'Route type': i[9]} for i in result]

            return HttpResponse(list_event)

        else:
            return HttpResponse('Event not found')


def user_authorization(request):
    if not request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'login.html')

        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponse('User is login')
            else:
                return HttpResponse('User not found / Wrong password or username. '
                                    '<br><a href="login" > Try again </a>'
                                    '<br><a href="registration" > Register new user </a>')
    else:
        return HttpResponse('<a href="logout" > Logout</a>')


def user_registration(request):
    if not request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'registration.html')

        if request.method == 'POST':
            user = User.objects.create_user(username=request.POST.get('username'),
                                            password=request.POST.get('password'),
                                            email=request.POST.get('email'),
                                            first_name=request.POST.get('first_name'),
                                            last_name=request.POST.get('last_name'))
            user.save()
            return HttpResponse('User is registered')
    else:
        return HttpResponse('<a href="logout" > Logout</a>')


def logout_user(request):
    logout(request)
    return redirect('/login')
