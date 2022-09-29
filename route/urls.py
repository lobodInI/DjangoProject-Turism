from django.urls import path
from . import views


app_name = 'route'

urlpatterns = [
    path('', views.route_filter, name='all_route'),
    path('<int:id>', views.route_info, name='route'),
    path('<int:id>/<str:review>', views.route_reviews, name='route_review'),
    path('add_route', views.route_add, name='add_route'),
    path('<int:id>/add_event', views.route_add_event, name='add_event'),
    path('<str:type>', views.route_filter, name='route_type'),
    path('<str:type>/<str:country>', views.route_filter, name='route_country'),
    path('<str:type>/<str:country>/<str:location>', views.route_filter, name='route_location')
]