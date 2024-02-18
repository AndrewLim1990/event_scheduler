from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect

from events.forms import RegistrationForm
from events.models import Event
from events.utils import create_event
from events.utils import string_to_date_time
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
                string_to_date_time(start)[0],
                string_to_date_time(end)[0],
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


def event_invite(request, uuid):
    event = get_object_or_404(Event, uuid=uuid)

    if request.method == 'POST':
        form = RegistrationForm(request.POST, event=event)
        if form.is_valid():
            # Process registration or sign-in
            # For new users, you might create a new User instance
            return redirect('event_detail', event_id=event.id)  # Redirect to event detail or confirmation page
    else:
        form = RegistrationForm(event=event)

    return render(request, 'events/invite.html', {'form': form, 'event': event})
