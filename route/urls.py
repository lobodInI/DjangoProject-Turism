from django.urls import path
from . import views


app_name = 'route'

urlpatterns = [
    path('', views.route_filter, name='show_filter_route'),
    path('info_route', views.route_info, name='info_route'),
    path('review', views.route_reviews, name='route_review'),
    path('add_route', views.route_add, name='add_route'),
    path('add_event', views.route_add_event, name='add_event'),
    path('info_event', views.event_info, name='info_event'),
    # path('route_filter', views.route_filter, name='route_filter'),
    # path('<str:route_type>/<str:country>', views.route_filter, name='route_country'),
    # path('<str:route_type>/<str:country>/<str:location>', views.route_filter, name='route_location')
]