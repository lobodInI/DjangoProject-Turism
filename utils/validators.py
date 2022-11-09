from datetime import datetime
from django.core.exceptions import ValidationError


def validate_event_date(value):
    try:
        date_check = datetime.strptime(str(value), "%Y-%m-%d")     # додатково "value" записав у str(). бо через datepicker datetime формат
    except BaseException:
        raise ValidationError("Incorrect date format")

    if datetime.today() > date_check:
        raise ValidationError("Enter the date correctly")


def validate_event_price(value):
    try:
        event_price = int(value)
    except BaseException:
        raise ValidationError("The price should be an integer")

    if event_price <= 0:
        raise ValidationError("Services are not free. Enter the price correctly")
