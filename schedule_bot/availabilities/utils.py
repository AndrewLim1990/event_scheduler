from availabilities.models import Availability
from collections import defaultdict
from django.contrib.auth.models import User
from events.models import UserEventTime
from events.utils import get_all_event_participants
from events.models import EventTime


def get_availabilities_for_participants(participants):
    """
    Returns a list of availabilities for all participants

    :param participants: list of Participant objects
    :return: list of Availability objects
    """
    availabilities = list()
    availability_models = Availability.__subclasses__()
    for availability_model in availability_models:
        availabilities += list(availability_model.objects.filter(user__in=participants))

    return availabilities


def get_users_declined(event_time):
    """
    Returns users that explicitly cannot attend event_time

    :param event_time:
    :param users:
    :return:
    """

    participants = get_all_event_participants(event_time.event)
    user_ids = list(UserEventTime.objects.filter(
        event_time=event_time,
        user__in=participants,
        explicit_response=UserEventTime.CANNOT_COME
    ).values_list("user_id", flat=True))
    users_declined = list(User.objects.filter(id__in=user_ids))

    return users_declined


def check_availabilities(event):
    """
    Checks availability of all members + host against proposed times

    :param event: an Event object
    :return: tuple of the form:
        (
            {
                event_time_id_1: [user_1, user_2],  <- list of users able to attend
                event_time_id_2: [user_1],
                event_time_id_3: [user_1, user_2]
                ...
                event_time_id_n: []
            },
            [event_time_id_1, event_time_id_3] <- list of EventTime id's that work for all participants
        )
    """
    # Gets all members + host member
    participants = get_all_event_participants(event)
    n_participants = len(participants)

    # Gets all availabilities
    availabilities = get_availabilities_for_participants(participants)

    # Gets suggested event times
    suggested_event_times = list(EventTime.objects.filter(event=event))

    # Compares implicit availabilities against suggested times
    availability_dict = defaultdict(list)
    times_that_work = list()
    for event_time in suggested_event_times:
        # Gets users that explicitly cannot attend event_time
        users_declined = get_users_declined(event_time)
        for availability in availabilities:
            is_available = availability.check_availability(event_time)
            has_explicitly_declined = availability.user in users_declined
            if is_available and not has_explicitly_declined:
                availability_dict[event_time.id].append(availability.user)
        everyone_is_available = len(availability_dict[event_time.id]) == n_participants
        if everyone_is_available:
            times_that_work.append(event_time.id)

    return availability_dict, times_that_work


def find_available_unseen_suggested_date(user_event):
    """
    Finds an UserEventTime that works for all Event participants
    """

    # Filters for event_times that work for everybody
    __, viable_event_times = check_availabilities(user_event.event)

    # Filters for unseen user_event_times
    valid_user_event_times = list(UserEventTime.objects.filter(
        user=user_event.user,
        event_time__in=viable_event_times,
        has_seen=False,
        is_active=False
    ))

    return valid_user_event_times
