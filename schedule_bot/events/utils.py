import datetime
import parsedatetime


def get_all_event_participants(event):
    """
    Returns all event members + host_member

    :param event: an Event objects to get all participants for
    :return: list of User objects
    """
    # Gets host and members
    host_member = [event.host_member]
    members = list(event.members.all())

    # Combines host and members
    participants = host_member + members

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
