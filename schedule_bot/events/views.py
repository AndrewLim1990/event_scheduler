from collections import defaultdict
from accounts.models import Member
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from events.forms import RegistrationForm
from events.models import Event, UserEvent, UserEventTime
from events.utils import create_event, convert_to_human_readable_times
from events.utils import string_to_date_time
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from events.forms import EventCreationForm
from django.urls import reverse
from datetime import timedelta

import pandas as pd
import requests


@api_view(['POST'])
def event_initialization(request):
    """
    API to create an event

    :param request:
    :return:
    """
    # Ensure the request is in JSON format
    if request.method == 'POST':
        # Extract data from the request
        user_id = request.data.get('user_id')
        event_name = request.data.get('event_name')
        event_times = request.data.get('event_times')

        # Processes event times (str -> datetime)
        proposed_times = []
        for start, end in event_times:
            proposed_times.append((
                string_to_date_time(start)[0],
                string_to_date_time(end)[0],
            ))

        # Creates Event and UserEvent associations for all participants
        host = Member.objects.get(id=user_id)

        event = create_event(
            host_user=host,
            event_name=event_name,
            invitees=[],
            proposed_times=proposed_times
        )

        # Dummy URL for the sake of example
        response_url = event.get_invite_url()
        response_url = request.build_absolute_uri(response_url)

        # Return the response URL
        return Response({
            "link": response_url,
            "event_id": event.id
        }, status=status.HTTP_201_CREATED)

    # Handle unsupported methods
    return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def event_invite(request, uuid):
    """
    View for event invite URL

    :param request:
    :param uuid:
    :return:
    """
    event = get_object_or_404(Event, uuid=uuid)

    if request.method == 'POST':
        form = RegistrationForm(request.POST, event=event)
        if form.is_valid():
            form.save()
            return redirect('event_detail', event_id=event.id)  # Redirect to event detail or confirmation page
    else:
        form = RegistrationForm(event=event)

    return render(request, 'events/invite.html', {'form': form, 'event': event})


@login_required
def event_detail(request, event_id):
    """
    Display the details of a specific event.

    :param request:
    :param event_id:
    :return:
    """
    event = get_object_or_404(Event, id=event_id)
    form = RegistrationForm(request.POST or None, event=event)

    # Checks to see if user is part of event
    is_participant = UserEvent.objects.filter(user=request.user, event=event).exists()
    if not is_participant:
        return render(request, 'events/event_access_denied.html', status=403)

    # Assuming UserEvent model links users to events, and you want to show attendees
    user_events = UserEvent.objects.filter(event=event)
    invite_url = event.get_invite_url()
    invite_url = request.build_absolute_uri(invite_url)

    # Obtains responses for event
    responses = pd.DataFrame(UserEventTime.objects.filter(
        event_time__event=event
    ).values(
        "user__id",
        "event_time__date_time_start",
        "event_time__date_time_end",
        "explicit_response",
    ))

    # Converts to humanreadable times
    suggested_times = [
        convert_to_human_readable_times(row["event_time__date_time_start"], row["event_time__date_time_end"])
        for idx, row in responses.iterrows()
    ]
    suggested_times = [x[0] + " to " + x[1] for x in suggested_times]
    responses["suggested_time"] = suggested_times
    suggested_times = list(set(suggested_times))

    response_dict = defaultdict(dict)
    for idx, row in responses.iterrows():
        response_dict[row["user__id"]][row["suggested_time"]] = row["explicit_response"]
    response_dict = dict(response_dict)

    if request.method == 'POST':
        if "remove_self" in request.POST:
            user_event = UserEvent.objects.get(
                user=request.user,
                event=event
            )
            user_event.delete()
        elif "add_self" in request.POST:
            user_event = UserEvent(
                user=request.user,
                event=event,
                is_required=True,
                is_host=False
            )
            user_event.save()
        elif "add_participant" in request.POST and form.is_valid():
            form.save()
        elif "remove_participant_id" in request.POST:
            user_event = UserEvent.objects.get(
                user=request.POST["remove_participant_id"],
                event=event
            )
            user_event.delete()
        return redirect('event_detail', event_id=event.id)  # Redirect to event detail or confirmation page

    return render(request, 'events/event_detail.html', {
        'event': event,
        'form': form,
        'user_events': user_events,
        'event_invite_url': invite_url,
        'is_participant': is_participant,
        'responses': response_dict,
        'suggested_times': suggested_times
    })


def create_event_view(request):
    """
    View to create an event

    :param request:
    :return:
    """
    if request.method == 'POST':
        form = EventCreationForm(request.POST)
        if form.is_valid():
            user_id = request.user.id
            event_name = form.cleaned_data['event_name']
            event_time_start = form.cleaned_data['event_times']
            event_duration = form.cleaned_data["event_duration"]
            event_time_end = event_time_start + timedelta(minutes=event_duration)

            # Convert event_times and invitee_ids to the required format
            event_times_list = [(str(event_time_start), str(event_time_end))]

            # Prepare the data for the API request
            data = {
                'user_id': user_id,
                'event_name': event_name,
                'event_times': event_times_list
            }

            # Make the API request
            api_endpoint = reverse('event_initialization')
            api_endpoint = request.build_absolute_uri(api_endpoint)
            response = requests.post(api_endpoint, json=data)

            if response.status_code == 201:
                # Redirect to the provided link or another success page
                event_id = response.json().get('event_id')
                event_detail_url = request.build_absolute_uri("/" + f"events/{event_id}")
                return redirect(event_detail_url)
            else:
                # Handle errors
                form.add_error(None, 'Failed to create event. Please try again.')

    else:
        form = EventCreationForm()

    return render(request, 'events/create_event.html', {'form': form})
