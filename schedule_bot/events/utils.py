import datetime
import parsedatetime

from django.contrib.auth.models import User
from events.models import Event


def get_all_event_participants(event):
    """
    Returns all event members + host_member

    :param event: an Event objects to get all participants for
    :return: list of User objects
    """
    user_ids = list(Event.objects.filter(id=event.id).values_list("users__user_id", flat=True))
    participants = list(User.objects.filter(id__in=user_ids))

    return participants


def string_to_date_time(input_string):
    """
    Translates input_string into datetime
    """
    # Convert string to structtime
    cal = parsedatetime.Calendar()
    struct_time, __ = cal.parse(input_string)

    # Convert structtime to datetime
    date_time = datetime.datetime(*struct_time[:6])

    return date_time
