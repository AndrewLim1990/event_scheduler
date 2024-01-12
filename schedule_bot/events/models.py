from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Event(models.Model):
    """
    Represents a specific event
    """
    name = models.CharField(max_length=512, null=True, default=None)


class EventTime(models.Model):
    """
    Represents a proposed event time
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="event_times")
    date_time_start = models.DateTimeField()
    date_time_end = models.DateTimeField()


class UserEventTime(models.Model):
    """
    Represents relation between a User and an EventTime
    """
    event_time = models.ForeignKey(EventTime, on_delete=models.CASCADE, related_name="user_event_time")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_event_time")
    is_active = models.BooleanField(default=False)
    has_seen = models.BooleanField(default=False)

    NO_RESPONSE = "waiting_response"
    CAN_COME = "can_come"
    CANNOT_COME = "cannot_come"
    STATE_CHOICES = [
        (NO_RESPONSE, "Has not answered for this event time"),
        (CAN_COME, "Has explicitly said they can come to this time slot"),
        (CANNOT_COME, "Has explicitly said they cannot come to this time slot"),
    ]

    explicit_response = models.CharField(choices=STATE_CHOICES, max_length=256, null=True, default=NO_RESPONSE)


class UserEvent(models.Model):
    """
    Represents a junction table between User and Event
    """
    WAITING_RESPONSE = "waiting_response"
    WAITING_SUGGESTION = "waiting_suggestion"
    WAITING_VALIDATION = "waiting_validation"
    WAITING_FOR_OTHERS = "waiting_for_others"
    IS_ATTENDING = "is_attending"
    IS_NOT_ATTENDING = "is_not_attending"
    NO_COMMUNICATION = "no_communication"
    STATE_CHOICES = [
        (WAITING_RESPONSE, "We are waiting for attendance from user"),
        (WAITING_SUGGESTION, "We are waiting for date suggestion from user"),
        (WAITING_VALIDATION, "We are waiting for date validation from user"),
        (WAITING_FOR_OTHERS, "We are waiting for other users to respond to suggestions"),
        (IS_ATTENDING, "User is able to attend event"),
        (IS_NOT_ATTENDING, "User has elected to not attend event"),
        (NO_COMMUNICATION, "We haven't sent any communication"),
    ]
    state = models.CharField(choices=STATE_CHOICES, max_length=256, null=True, default=NO_COMMUNICATION)

    user = models.ForeignKey(User, related_name="events", on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name="users", on_delete=models.CASCADE)
    is_required = models.BooleanField()
    is_host = models.BooleanField()


class SuggestedDate(models.Model):
    """
    Represents a text from a user suggesting a date
    """
    user_event = models.ForeignKey(UserEvent, related_name="suggested_date", on_delete=models.CASCADE)
    is_verified = models.BooleanField()
    is_active = models.BooleanField()
    input_text = models.CharField(max_length=256)
    interpreted_start = models.DateTimeField()
    interpreted_end = models.DateTimeField()
