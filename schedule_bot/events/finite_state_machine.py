from availabilities.utils import check_availabilities
from availabilities.utils import find_available_unseen_suggested_date
from distutils.util import strtobool
from django.contrib.auth.models import User

from communications.utils import send_message
from events.models import EventTime
from events.models import UserEvent
from events.models import UserEventTime
from events.models import SuggestedDate
from events.utils import get_avg_event_duration
from events.utils import string_to_date_time


def get_current_active_user_event_time(user_event):
    """
    """
    user_event_time = UserEventTime.objects.get(
        user=user_event.user,
        event_time__event=user_event.event,
        is_active=True
    )
    return user_event_time


def send_suggestion_text(user_event_time):
    """
    """
    # Gets start and end times
    event_time_start = user_event_time.event_time.date_time_start
    event_time_end = user_event_time.event_time.date_time_end

    # Sends text
    username = user_event_time.user.username
    text = f"{username}, would {event_time_start} to {event_time_end} work for you?"

    send_message(
        user=user_event_time.user,
        event=user_event_time.event_time.event,
        text=text
    )


def update_user_event_time_states(user_event_time, is_active, has_seen, explicit_response=UserEventTime.NO_RESPONSE):
    """
    """
    # Updates user event time status
    user_event_time.is_active = is_active
    user_event_time.has_seen = has_seen
    user_event_time.explicit_response = explicit_response
    user_event_time.save()


def update_user_event_state(user_event, state):
    """
    """
    user_event.state = state
    user_event.save()
    return state


class UserEventMachine:
    def __init__(self, user_event):
        self.states = {
            UserEvent.NO_COMMUNICATION: NoCommunicationState(),
            UserEvent.WAITING_RESPONSE: WaitingResponseState(),
            UserEvent.WAITING_VALIDATION: WaitingValidationState(),
            UserEvent.WAITING_FOR_OTHERS: WaitingForOthersState(),
            UserEvent.WAITING_SUGGESTION: WaitingSuggestionState(),
        }
        self.user_event = user_event
        self.state = self.states[self.user_event.state]

    def set_state(self, next_state):
        self.state = self.states[next_state]
        self.state.execute(self.user_event)
        print(f"{self.user_event.user}'s new state: {next_state}")

    def send_initial_text(self):
        try:
            self.state.send_initial_text(self)
        except AttributeError:
            raise NotImplementedError(f"Cannot send_initial_text while in {self.state.state_name} state")

    def process_input_text(self, input_text):
        try:
            self.state.process_input_text(self, self.user_event, input_text)
        except AttributeError:
            raise NotImplementedError(f"Cannot process_input_text while in {self.state.state_name} state")

    def invite_user(self, identifier, identifier_type="phone_number", is_required=True):
        """
        :param identifier:
        :param identifier_type:
        :param is_required:
        :return:
        """
        event = self.user_event.event
        if identifier_type == "phone_number":
            invitee, __ = User.objects.get_or_create(user_info__phone_number=identifier)
        elif identifier_type == "email":
            invitee, __ = User.objects.get_or_create(email=identifier)
        elif identifier_type == "username":
            invitee, __ = User.objects.get_or_create(username=identifier)
        else:
            raise NotImplementedError(f"Cannot invite user of identifier_type: {identifier_type}")
        invitee_user_event, __ = UserEvent.objects.update_or_create(
            user=invitee,
            event=event,
            defaults={"is_required": is_required, "is_host": False}
        )
        invitee_user_event_machine = UserEventMachine(invitee_user_event)
        invitee_user_event_machine.send_initial_text()


class NoCommunicationState:
    def __init__(self):
        self.state_name = UserEvent.NO_COMMUNICATION

    @staticmethod
    def send_initial_text(machine):
        """
        :param machine:
        :param user_event:
        :return:
        """
        user_event_times = find_available_unseen_suggested_date(machine.user_event)
        no_viable_times = len(user_event_times) == 0

        if no_viable_times:
            # Transition to next state: WAITING_SUGGESTION
            machine.set_state(UserEvent.WAITING_SUGGESTION)
        else:
            # Transition to next state: WAITING_RESPONSE
            machine.set_state(UserEvent.WAITING_RESPONSE)


class WaitingResponseState:
    def __init__(self):
        self.state_name = UserEvent.WAITING_RESPONSE

    def execute(self, user_event):
        # Gets start and end times
        user_event_time = find_available_unseen_suggested_date(user_event)[0]

        # Sends text
        send_suggestion_text(user_event_time)
        update_user_event_time_states(user_event_time, is_active=True, has_seen=True)
        user_event_state = update_user_event_state(user_event, state=self.state_name)

    @staticmethod
    def process_input_text(machine, user_event, input_text):
        """
        :param machine:
        :param user_event:
        :param input_text:
        :return:
        """
        # Processes input text
        explicit_response = UserEventTime.CAN_COME if strtobool(input_text) else UserEventTime.CANNOT_COME
        user_event_time = get_current_active_user_event_time(user_event)
        update_user_event_time_states(
            user_event_time,
            is_active=False,
            has_seen=True,
            explicit_response=explicit_response
        )

        # Looks for more unseen new UserEventTime
        unseen_user_event_times = find_available_unseen_suggested_date(user_event)
        has_unseen_user_event_times = len(unseen_user_event_times) > 0
        if has_unseen_user_event_times:
            # Transition to next state: WAITING_RESPONSE
            machine.set_state(UserEvent.WAITING_RESPONSE)
        else:
            # Checks for viable times
            __, viable_event_times = check_availabilities(user_event.event)
            no_viable_event_times = len(viable_event_times) < 1
            if no_viable_event_times:
                # Transition to next state: WAITING_SUGGESTION
                machine.set_state(UserEvent.WAITING_SUGGESTION)
            else:
                # Transition to next state: WAITING_FOR_OTHERS
                machine.set_state(UserEvent.WAITING_FOR_OTHERS)


class WaitingSuggestionState:
    def __init__(self):
        self.state_name = UserEvent.WAITING_SUGGESTION

    def execute(self, user_event):
        """
        :param machine:
        :param user_event:
        :return:
        """
        text = "There are no viable event times, can you please suggest a time that works for you?"
        send_message(
            user=user_event.user,
            event=user_event.event,
            text=text
        )
        update_user_event_state(user_event, state=UserEvent.WAITING_SUGGESTION)

    def process_input_text(self, machine, user_event, suggestion_text):
        """
        Compares suggested_event_time against all members in event

        :param machine:
        :param user_event:
        :param suggestion_text:
        :return:
        """
        # Interprets input text
        suggested_start = string_to_date_time(suggestion_text)
        duration = get_avg_event_duration(user_event.event)
        suggested_end = suggested_start + duration

        # Saves suggested date
        suggested_date = SuggestedDate()
        suggested_date.user_event = user_event
        suggested_date.is_active = True
        suggested_date.is_verified = False
        suggested_date.input_text = suggestion_text
        suggested_date.interpreted_start = suggested_start
        suggested_date.interpreted_end = suggested_end
        suggested_date.save()

        # Sends text
        text = f"Did you mean: {suggested_start} - {suggested_end}?"
        send_message(
            user=user_event.user,
            event=user_event.event,
            text=text
        )

        # Updates state
        machine.set_state(UserEvent.WAITING_VALIDATION)


class WaitingForOthersState:
    def __init__(self):
        self.state_name = UserEvent.WAITING_FOR_OTHERS

    def execute(self, user_event):
        update_user_event_state(user_event, state=UserEvent.WAITING_FOR_OTHERS)


class WaitingValidationState:
    def __init__(self):
        self.state_name = UserEvent.WAITING_VALIDATION

    def execute(self, user_event):
        update_user_event_state(user_event, state=UserEvent.WAITING_VALIDATION)

    @staticmethod
    def process_input_text(machine, user_event, validation_response):
        """
        :param machine:
        :param user_event:
        :param validation_response:
        :return:
        """
        # Processes input text
        is_valid_response = strtobool(validation_response)

        # Saves if correct
        if is_valid_response:
            # Marks suggested date as valid
            suggested_date = SuggestedDate.objects.get(user_event=user_event, is_verified=False, is_active=True)
            suggested_date.is_active = False
            suggested_date.is_verified = True
            suggested_date.save()

            # Adds EventTime
            event_time = EventTime()
            event_time.event = user_event.event
            event_time.date_time_start = suggested_date.interpreted_start
            event_time.date_time_end = suggested_date.interpreted_end
            event_time.save()

            # Provides attendance for suggester
            user_event_time = UserEventTime.objects.get(event_time=event_time, user=user_event.user)
            update_user_event_time_states(
                user_event_time=user_event_time,
                is_active=False,
                has_seen=True,
                explicit_response=UserEventTime.CAN_COME
            )

            # Updates state
            machine.set_state(UserEvent.WAITING_FOR_OTHERS)
        else:
            suggested_date = SuggestedDate.objects.get(user_event=user_event, is_verified=False, is_active=True)
            suggested_date.is_active = False
            suggested_date.is_verified = False
            suggested_date.save()

            text = (
                "Sorry, can you please provide your suggested time in the format similar to:\n",
                "2022-1-12 4PM to 2022-1-12 7PM "
            )
            send_message(user=user_event.user, event=user_event.event, text=text)

            # Updates state
            machine.set_state(UserEvent.WAITING_SUGGESTION)




