from events.models import UserEvent
from events.models import Event
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
        member_id = request.data.get('member_id')
        event_name = request.data.get('event_name')
        event_times = request.data.get('event_times')
        invitee_ids = request.data.get('invitee_ids')

        # Process the data (this is where you would add your logic)
        # For example, create an event in your database

        # Dummy URL for the sake of example
        response_url = "https://example.com/event/123"

        # Return the response URL
        return Response({"link": response_url}, status=status.HTTP_201_CREATED)

    # Handle unsupported methods
    return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
