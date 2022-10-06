from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from route import models


def route_filter(request):
    if request.method == 'GET':
        country_list = set()
        country_objs = models.Places.objects.all()
        for itm in range(len(country_objs)):
            country_list.add(country_objs[itm].name_country)
        return render(request, 'route_filter.html', {'country_list': country_list})

    if request.method == 'POST':
        query_filter = {'route_type': request.POST.get('route_type')}
        if request.POST.get('country') != 'ALL':
            query_filter['country'] = request.POST.get('country')
        if request.POST.get('location') != '':
            query_filter['location'] = request.POST.get('location')

        result = models.Route.objects.all().filter(**query_filter)
        if result:
            return HttpResponse([{'id': i.id,
                                  'starting_point': i.starting_point,
                                  'stopping_point': i.stopping_point,
                                  'destination': i.destination,
                                  'country': i.country,
                                  'location': i.location,
                                  'description': i.description,
                                  'duration': i.duration,
                                  'route_type': i.route_type} for i in result])
        else:
            return HttpResponse('Routes not found')


def route_info(request):
    if request.method == 'GET':
        return render(request, 'info_route.html')

    if request.method == 'POST':
        result = models.Route.objects.all().filter(id=request.POST.get('id_route'))
        if result:

            route_events = models.Event.objects.all().filter(id_route=request.POST.get('id_route'))
            if route_events:
                return HttpResponse([{'INFO ABOUT ROUTE': {'id': i.id,
                                                           'starting_point': i.starting_point,
                                                           'stopping_point': i.stopping_point,
                                                           'destination': i.destination,
                                                           'country': i.country,
                                                           'location': i.location,
                                                           'description': i.description,
                                                           'duration': i.duration,
                                                           'route_type': i.route_type} for i in result},
                                     {'ROUTE EVENTS': {'id': i.id,
                                                       'id_route': i.id_route,
                                                       'event_admin': i.event_admin,
                                                       'approved_users': i.approved_users,
                                                       'pending_users': i.pending_users,
                                                       'start_date': i.start_date,
                                                       'price': i.price} for i in route_events},
                                     '<a href="add_event" >ADD NEW EVENT</a>'])

            else:
                return HttpResponse([{'INFO ABOUT ROUTE': {'id': i.id,
                                                           'starting_point': i.starting_point,
                                                           'stopping_point': i.stopping_point,
                                                           'destination': i.destination,
                                                           'country': i.country,
                                                           'location': i.location,
                                                           'description': i.description,
                                                           'duration': i.duration,
                                                           'route_type': i.route_type} for i in result},
                                     {'ROUTE EVENTS': 'NOT FOUND INFORMATION ABOUT ROUTE EVENT'},
                                     '<a href="add_event" >ADD NEW EVENT</a>'])

        else:
            return HttpResponse('Not found route')


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
        result = models.Event.objects.all().filter(id=request.POST.get('id_event'))
        if result:
            return HttpResponse([{'id': i.id,
                                  'id_route': i.id_route,
                                  'event_admin': i.event_admin,
                                  'approved_users': i.approved_users,
                                  'pending_users': i.pending_users,
                                  'start_date': i.start_date,
                                  'price': i.price} for i in result])
        else:
            return HttpResponse('Not found event')


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
