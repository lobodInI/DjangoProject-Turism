from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def route_filter(request, route_type=None, country=None, location=None):
    return HttpResponse('Ok')


def route_info(request, route_id):
    return HttpResponse('Route info')


def route_add(request):
    return HttpResponse('Creating a route')


def route_reviews(request, route_id):
    return HttpResponse('Route review')


def route_add_event(request, route_id):
    return HttpResponse('Info event')


def event_handler(request, id_event):
    return HttpResponse('Info event')