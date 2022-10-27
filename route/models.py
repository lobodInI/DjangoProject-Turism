import validators
from django.db import models
from django.utils.translation import gettext_lazy


class Places(models.Model):
    name = models.CharField(max_length=50)
    name_country = models.CharField(max_length=50, null=False)


class Route(models.Model):
    starting_point = models.IntegerField()
    stopping_point = models.CharField(max_length=50)
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
    event_users = models.CharField(max_length=50, null=True)
    start_date = models.DateField(validators=[validators.validate_event_date])
    price = models.IntegerField(validators=[validators.validate_event_price])


class Review(models.Model):
    route_id = models.IntegerField()
    review_text = models.TextField()
    review_rate = models.IntegerField()
