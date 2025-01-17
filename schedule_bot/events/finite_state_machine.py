import pandas as pd

from availabilities.utils import check_availabilities, process_str_to_bool
from availabilities.utils import find_available_unseen_suggested_date
from communications.utils import send_message
from accounts.models import Member
from events.models import EventTime
from events.models import UserEvent
from events.models import UserEventTime
from events.models import SuggestedDate
from events.utils import get_avg_event_duration, get_assumed_start_time
from events.utils import string_to_date_time
from events.utils import convert_to_human_readable_times


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
    host_name = UserEvent.objects.get(
        event=user_event_time.event_time.event,
        is_host=True
    ).user.username
    event_name = user_event_time.event_time.event.name
    start_str, end_str = convert_to_human_readable_times(event_time_start, event_time_end)
    text = (
        f"Hi {username}! You've been invited to {event_name} by {host_name}. "
        f"Would {start_str} to {end_str} work for you?"
    )

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
            invitee, __ = Member.objects.get_or_create(user_info__phone_number=identifier)
        elif identifier_type == "email":
            invitee, __ = Member.objects.get_or_create(email=identifier)
        elif identifier_type == "username":
            invitee, __ = Member.objects.get_or_create(username=identifier)
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
        try:
            explicit_response = UserEventTime.CAN_COME if process_str_to_bool(input_text) else UserEventTime.CANNOT_COME
        except ValueError:
            send_message(
                user=user_event.user,
                event=user_event.event,
                text=f"Sorry, we could not process '{input_text}', please respond with 'yes' or 'no'"
            )
            return

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
        suggested_start, contains_time = string_to_date_time(suggestion_text)
        if not contains_time:
            assumed_time = get_assumed_start_time(user_event)
            suggested_start = suggested_start.replace(
                hour=assumed_time.hour,
                minute=assumed_time.minute,
                second=assumed_time.second,
                microsecond=assumed_time.microsecond
            )

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
        readable_start, readable_end = convert_to_human_readable_times(suggested_start, suggested_end)
        text = f"Did you mean: {readable_start} - {readable_end}?"
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
        unanswered_usernames = UserEvent.objects.filter(
            event=user_event.event
        ).exclude(
            state=UserEvent.WAITING_FOR_OTHERS
        ).values_list("user__username", flat=True)

        if unanswered_usernames:
            text = "Great! Thank you fo1`r your response, we are now waiting on others to reply:"
            for user_name in unanswered_usernames:
                text += f"\n - {user_name}"
        else:
            user_event_time_df = pd.DataFrame(UserEventTime.objects.filter(
                event_time__event=user_event.event
            ).values())
            user_event_time_df = user_event_time_df.groupby("event_time_id")["explicit_response"].apply(list)
            user_event_time_df = user_event_time_df.reset_index()
            user_event_time_df["all_can_come"] = user_event_time_df["explicit_response"].apply(
                lambda responses: all([response == UserEventTime.CAN_COME for response in responses])
            )
            valid_event_time_id = user_event_time_df.query("all_can_come")["event_time_id"].values[0]
            event_time = EventTime.objects.get(id=valid_event_time_id)
            start, end = convert_to_human_readable_times(event_time.date_time_start, event_time.date_time_end)
            text = f"Great! Looks like you guys are set for: {start} - {end}"

        send_message(
            user=user_event.user,
            event=user_event.event,
            text=text
        )


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
        try:
            is_valid_response = process_str_to_bool(validation_response)
        except ValueError:
            send_message(
                user=user_event.user,
                event=user_event.event,
                text=f"Sorry, we could not process '{validation_response}', please respond with 'yes' or 'no'"
            )
            return

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
