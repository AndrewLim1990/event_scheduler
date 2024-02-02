from datetime import datetime
from django.contrib.auth.models import User
from events.utils import create_event
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['POST'])
def event_initialization(request):
    """
    :param request:
    :return:
    """
    # Ensure the request is in JSON format
    if request.method == 'POST':
        # Extract data from the request
        user_id = request.data.get('user_id')
        event_name = request.data.get('event_name')
        event_times = request.data.get('event_times')
        invitee_ids = request.data.get('invitee_ids')

        # Processes event times (str -> datetime)
        proposed_times = []
        for start, end in event_times:
            proposed_times.append((
                datetime.strptime(start, '%m/%d/%y %H:%M:%S'),
                datetime.strptime(end, '%m/%d/%y %H:%M:%S')
            ))

        # Creates Event and UserEvent associations for all participants
        host = User.objects.get(id=user_id)
        invitees = list(User.objects.filter(id__in=invitee_ids))
        create_event(
            host_user=host,
            event_name=event_name,
            invitees=invitees,
            proposed_times=proposed_times
        )

        # Dummy URL for the sake of example
        response_url = "https://example.com/event/123"

        # Return the response URL
        return Response({"link": response_url}, status=status.HTTP_201_CREATED)

    # Handle unsupported methods
    return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
