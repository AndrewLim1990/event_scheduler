from django.db import models
from django.contrib.auth.models import User


class Availability(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(default=None, null=True, max_length=512)
    is_available = models.BooleanField()

    def check_availability(self, suggested_date):
        """
        Checks availability against suggested date

        :param suggested_date:
        :return:
        """
        raise NotImplemented


class DateAvailability(Availability):
    date_time_start = models.DateTimeField()
    date_time_end = models.DateTimeField()

    def check_availability(self, suggested_date):
        """
        Checks availability against suggested date

        :param suggested_date:
        :return:
        """
        return suggested_date


class RepeatedDateAvailability(DateAvailability):
    is_repeated_weekly = models.BooleanField(default=False)
    is_repeated_monthly = models.BooleanField(default=False)


class WeekAvailability(Availability):
    WEEKEND = "weekend"
    WEEKDAY = "weekday"
    WEEK_AVAILABILITY_CHOICES = [
        (WEEKEND, "Weekend"),
        (WEEKDAY, "Weekday"),
    ]
    week_availability = models.CharField(choices=WEEK_AVAILABILITY_CHOICES, max_length=256)
