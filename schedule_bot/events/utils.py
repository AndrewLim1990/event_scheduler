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
