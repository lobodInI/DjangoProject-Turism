import os
import json

from datetime import datetime
from bson import ObjectId
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from utils.mongo_utils import MongoDBConnection
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
                                end_point.name,
                                route_route.id
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
                           "End point": i[6],
                           "ID Route": i[7]} for i in result_query]

            p = Paginator(list_route, 2)
            try:
                num_page = int(request.POST.get('page', default=1))
            except ValueError:
                return HttpResponse('Fatal error. The page number must be an integer', status=404)

            if num_page > p.num_pages:
                num_page = 1
            select_page = p.get_page(num_page)

            return HttpResponse([select_page.object_list, f"<br>Number page: {num_page}",
                                 '<br><a href="info_route" >SELECT ROUTE INFORMATION</a>'])
        else:
            return HttpResponse('Routes not found', status=404)


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

            with MongoDBConnection(os.environ.get('DB_USERNAME'), os.environ.get('DB_PASSWORD'),
                                   os.environ.get('DB_HOST')) as db:
                collection = db['Stopping point']
                stopping_point = collection.find_one({'_id': ObjectId(select_route[0]['Stopping point'])})

            select_route[0]['Stopping point'] = stopping_point['points']  # замінюємо ІД зупинок на повну інформацію

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
            return HttpResponse('Route not found', status=404)


def route_add(request):
    if request.user.has_perm('route.add_route'):
        if request.method == 'GET':
            places_list = []
            country_list = set()
            place_objs = models.Places.objects.all()
            for itm in range(len(place_objs)):
                places_list.append(place_objs[itm].name)
                country_list.add(place_objs[itm].name_country)
            country_list.remove('ALL')  # в створенні маршруту ALL не має бути
            return render(request, 'add_route.html', {'places_list': places_list,
                                                      'country_list': country_list,
                                                      'limit_duration': range(1, 11)})

        if request.method == 'POST':
            starting_point = request.POST.get('starting_point')
            destination = request.POST.get('destination')
            country = request.POST.get('country')
            stopping_point = request.POST.get('stopping_point')
            location = request.POST.get('location')
            description = request.POST.get('description')
            duration = request.POST.get('duration')
            route_type = request.POST.get('route_type')

            stopping_list = json.loads(stopping_point)

            with MongoDBConnection(os.environ.get('DB_USERNAME'), os.environ.get('DB_PASSWORD'),
                                   os.environ.get('DB_HOST')) as db:
                collection = db['Stopping point']
                id_stopping_point = collection.insert_one({"points": stopping_list}).inserted_id

            start_obj = models.Places.objects.get(name=starting_point)
            destination_obj = models.Places.objects.get(name=destination)
            new_route = models.Route(starting_point=start_obj.id,
                                     stopping_point=id_stopping_point,
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
        return render(request, 'route_show_review.html')

    if request.method == 'POST':
        result = models.Review.objects.all().filter(route_id=request.POST.get('id_route'))
        if result:
            return HttpResponse([{'route_id': i.route_id,
                                  'review_text': i.review_text,
                                  'review_rate': i.review_rate} for i in result])
        else:
            return HttpResponse('Not found reviews', status=404)


def route_add_review(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            all_id_route = []
            route_objs = models.Route.objects.all()
            for itm in range(len(route_objs)):
                all_id_route.append(route_objs[itm].id)
            return render(request, 'route_review_add.html', {"all_id_route": all_id_route,
                                                             'rating_range': range(1, 11)})

        if request.method == 'POST':
            id_route = request.POST.get('id_route')
            user_review = request.POST.get('user_review')
            user_rating = request.POST.get('user_rating')

            new_review = models.Review(route_id=id_route,
                                       review_text=user_review,
                                       review_rate=user_rating)
            new_review.save()
            return HttpResponse("Thanks for feedback. Review added")
    else:
        return HttpResponse('You are not authorized', status=401)


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
                                     event_users={})
            try:
                new_event.full_clean()
                new_event.save()
            except ValidationError:
                return HttpResponse('Check correct date or/and check price')

            return HttpResponse('Event added')
    else:
        return HttpResponse('Not allowed to add event', status=401)


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
                               route.route_type,
                               event.event_users

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
                           'Route type': i[9],
                           'Event users': i[10]} for i in result]

            with MongoDBConnection(os.environ.get('DB_USERNAME'), os.environ.get('DB_PASSWORD'),
                                   os.environ.get('DB_HOST')) as db:
                collection_point = db['Stopping point']
                stopping_point = collection_point.find_one({'_id': ObjectId(list_event[0]['Stopping point'])})

                collection_user = db['event_users']
                id_event_users = collection_user.find_one({"_id": ObjectId(list_event[0]['Event users'])})

            list_event[0]['Stopping point'] = stopping_point['points']  # замінюємо ІД зупинок на повну інформацію

            users_accepted = User.objects.filter(pk__in=id_event_users['accepted'])
            users_pending = User.objects.filter(pk__in=id_event_users['pending'])

            list_event[0]['Accepted users'] = [{f"ID {i.id}": i.username for i in users_accepted}]
            list_event[0]['Pending users'] = [{f"ID {i.id}": i.username for i in users_pending}]

            return HttpResponse(list_event)

        else:
            return HttpResponse('Event not found', status=404)


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
        return HttpResponse('<a href="logout" > Logout</a>', )


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


def add_me_to_event(request, id_event):
    user = request.user.id
    event = models.Event.objects.filter(id=id_event).first()

    with MongoDBConnection(os.environ.get('DB_USERNAME'), os.environ.get('DB_PASSWORD'),
                           os.environ.get('DB_HOST')) as db:
        event_users = db['event_users']
        all_event_user = event_users.find_one({"_id": ObjectId(event.event_users)})

        if user in all_event_user['pending'] or user in all_event_user['accepted']:
            return HttpResponse('You are in pending/accepted users')
        else:
            all_event_user['pending'].append(user)
            event_users.update_one({"_id": ObjectId(event.event_users)}, {"$set": all_event_user}, upsert=False)

        return HttpResponse('Excellent. You have added yourself to the event. Wait for confirmation')


def event_accept_user(request, id_event):
    if request.method == "GET":
        if request.user.is_superuser:
            event = models.Event.objects.filter(id=id_event).first()

            with MongoDBConnection(os.environ.get('DB_USERNAME'), os.environ.get('DB_PASSWORD'),
                                   os.environ.get('DB_HOST')) as db:
                collection = db['event_users']
                all_event_user = collection.find_one({'_id': ObjectId(event.event_users)})

            return render(request, "user_confirmation.html", {"pending_users": all_event_user['pending']})
        else:
            return HttpResponse("Not allowed to event handling")

    if request.method == "POST":
        if request.POST.get("selected_id_user") is not None:

            event = models.Event.objects.filter(id=id_event).first()
            selected_user = int(request.POST.get("selected_id_user"))

            with MongoDBConnection(os.environ.get('DB_USERNAME'), os.environ.get('DB_PASSWORD'),
                                   os.environ.get('DB_HOST')) as db:
                collection = db['event_users']
                all_event_user = collection.find_one({"_id": ObjectId(event.event_users)})

                all_event_user["pending"].remove(selected_user)
                all_event_user["accepted"].append(selected_user)

                collection.update_one({"_id": ObjectId(event.event_users)}, {"$set": all_event_user}, upsert=False)

            return HttpResponse(f'User with ID : {selected_user} is accepted')
        else:
            return HttpResponse('No users selected./No pending users in the event')
