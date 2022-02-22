import datetime

import pandas as pd
import parsedatetime

from django.contrib.auth.models import User
from events.models import Event, EventTime, UserEvent, UserEventTime


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


def get_avg_event_duration(event):
    event_time_df = pd.DataFrame(EventTime.objects.filter(event=event).values())
    event_time_df["duration"] = event_time_df["date_time_end"] - event_time_df["date_time_start"]
    average_duration = event_time_df["duration"].mean()
    return average_duration


def create_event(host_user, event_name, invitees, proposed_times):
    """
    Initializes event

    :param host_user:
    :param event_name:
    :param invitees:
    :param proposed_times:
    :return:
    """
    # Generates event
    event, __ = Event.objects.get_or_create(
        name=event_name,
    )

    # Connects host users to event
    user_event, __ = UserEvent.objects.update_or_create(
        user=host_user,
        event=event,
        defaults={
            "is_host": True,
            "is_required": True
        }
    )
    user_event.state = UserEvent.WAITING_FOR_OTHERS
    user_event.save()

    # Connects invitees to event
    for invitee in invitees:
        UserEvent.objects.update_or_create(
            user=invitee,
            event=event,
            defaults={
                "is_host": False,
                "is_required": True
            }
        )

    # Generates proposed times
    for proposed_start, proposed_end in proposed_times:
        EventTime.objects.update_or_create(
            event=event,
            date_time_start=proposed_start,
            defaults={"date_time_end": proposed_end},
        )

    # Provides explicit response for host_user
    user_event_times = UserEventTime.objects.filter(
        user=user_event.user,
        event_time__event=event
    )
    for user_event_time in user_event_times:
        user_event_time.explicit_response = UserEventTime.CAN_COME
        user_event_time.save()

