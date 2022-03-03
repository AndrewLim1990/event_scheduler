from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


class Availability(models.Model):
    """
    Represents User availability independent of a specific event
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(default=None, null=True, max_length=512)
    is_available = models.BooleanField()

    def check_availability(self, event_time):
        """
        Checks availability against suggested date

        :param suggested_date:
        :return:
        """
        raise NotImplemented


class DateAvailability(Availability):
    date_time_start = models.DateTimeField()
    date_time_end = models.DateTimeField()

    def check_availability(self, event_time):
        """
        Checks availability against suggested date

        :param suggested_date:
        :return:
        """
        event_start = event_time.date_time_start
        event_end = event_time.date_time_end
        availability_start = self.date_time_start
        availability_end = self.date_time_end

        if self.is_available:
            is_available = (availability_start <= event_start) and (availability_end >= event_end)
        else:
            is_not_available = (
                ((availability_start <= event_start) and (availability_end > event_start)) or  # Can't make start
                ((availability_start >= event_start) and (availability_end <= event_end)) or  # Can't make middle
                ((availability_start < event_end) and (availability_end >= event_end)) or  # Can't make end
                ((availability_start <= event_start) and (availability_end >= event_end))  # Can't make entire event
            )
            is_available = not is_not_available

        return is_available


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


class UserInformation(models.Model):
    user = models.OneToOneField(User, related_name="user_information", on_delete=models.CASCADE)
    phone_number = PhoneNumberField(null=True, unique=True, default=None)
