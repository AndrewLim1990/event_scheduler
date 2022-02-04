from availabilities.models import Availability
from events.utils import get_all_event_participants
from collections import defaultdict
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


def check_availabilities(event):
    """
    Checks availability of all members + host against proposed times

    :param event: an Event object
    :return: tuple of the form:
        (
            {
                event_time_id_1: [username_1, username_2],  <- list of usernames able to attend
                event_time_id_2: [username_1],
                event_time_id_3: [username_1, username_2]
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

    # Compares availabilities against suggested times
    availability_dict = defaultdict(list)
    times_that_work = list()
    for event_time in suggested_event_times:
        for availability in availabilities:
            is_available = availability.check_availability(event_time)
            if is_available:
                availability_dict[event_time.id].append(availability.user.username)
        everyone_is_available = len(availability_dict[event_time.id]) == n_participants
        if everyone_is_available:
            times_that_work.append(event_time.id)

    return availability_dict, times_that_work
