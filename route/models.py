from django.db import models
from django.utils.translation import gettext_lazy
# Create your models here.


class Places(models.Model):
    name = models.CharField(max_length=50)


class Route(models.Model):
    starting_point = models.IntegerField()
    stopping_point = models.JSONField()
    destination = models.IntegerField()
    country = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    description = models.TextField()
    duration = models.IntegerField()

    class RouteType(models.TextChoices):
        car_ride = 'Car', gettext_lazy('Car')
        on_foot = 'Foot', gettext_lazy('Foot')
        bike_ride = 'Bike', gettext_lazy('Bike')

    route_type = models.CharField(
        max_length=20,
        choices=RouteType.choices,
        default=RouteType.on_foot
    )


class Event(models.Model):
    id_route = models.IntegerField()
    event_admin = models.IntegerField()
    approved_users = models.JSONField()
    pending_users = models.JSONField()
    start_date = models.DateField()
    price = models.IntegerField()
