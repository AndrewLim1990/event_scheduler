from distutils.util import strtobool

from availabilities.utils import find_available_unseen_suggested_date, check_availabilities
from events.models import UserEvent
from events.models import UserEventTime


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
    print(f"Would {event_time_start} to {event_time_end} work for you?")


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
            # UserEvent.WAITING_VALIDATION: WaitingValidationState(),
            UserEvent.WAITING_FOR_OTHERS: WaitingForOthersState(),
            UserEvent.WAITING_SUGGESTION: WaitingSuggestionState(),
        }
        self.user_event = user_event
        self.state = self.states[self.user_event.state]

    def set_state(self, next_state, user_event_time):
        self.state = next_state
        self.state.execute(self, self.user_event, user_event_time)

    def send_initial_text(self):
        try:
            self.state.send_initial_text(self, self.user_event)
        except AttributeError:
            raise NotImplementedError(f"Cannot send_initial_text while in {self.state.state_name} state")

    def process_input_text(self, input_text):
        try:
            self.state.process_input_text(self, self.user_event, input_text)
        except AttributeError:
            raise NotImplementedError(f"Cannot process_input_text while in {self.state.state_name} state")


class NoCommunicationState:
    def __init__(self):
        self.state_name = UserEvent.NO_COMMUNICATION

    @staticmethod
    def send_initial_text(machine, user_event):
        """
        :param machine:
        :param user_event:
        :return:
        """
        # Gets start and end times
        user_event_time = find_available_unseen_suggested_date(user_event)[0]

        # Transition to next state
        machine.state = WaitingResponseState()
        machine.state.execute(machine, user_event, user_event_time)


class WaitingResponseState:
    def __init__(self):
        self.state_name = UserEvent.WAITING_RESPONSE

    def execute(self, machine, user_event, user_event_time):
        # Sends text
        send_suggestion_text(user_event_time)
        update_user_event_time_states(user_event_time, is_active=True, has_seen=True)
        user_event_state = update_user_event_state(user_event, state=self.state_name)
        print(f"New State: {user_event_state}")

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
            # Sends suggested text
            user_event_time = unseen_user_event_times[0]
            send_suggestion_text(user_event_time)

            # Transition to next state: WAITING_RESPONSE
            machine.state = WaitingResponseState()
            machine.state.execute(machine, user_event, user_event_time)
        else:
            # Checks for viable times
            __, viable_event_times = check_availabilities(user_event.event)
            no_viable_event_times = len(viable_event_times) < 1
            if no_viable_event_times:
                # Transition to next state: WAITING_SUGGESTION
                machine.state = WaitingSuggestionState()
                machine.state.execute(machine, user_event)
            else:
                # Transition to next state: WAITING_FOR_OTHERS
                machine.state = WaitingForOthersState()
                machine.state.execute(machine, user_event)


class WaitingSuggestionState:
    def __init__(self):
        self.state_name = UserEvent.WAITING_SUGGESTION

    def execute(self, machine, user_event):
        """
        :param machine:
        :param user_event:
        :return:
        """
        print("There are no viable event times, can you please suggest a time that works for you?")
        update_user_event_state(user_event, state=UserEvent.WAITING_SUGGESTION)
        print(f"New State: {self.state_name}")

    def process_suggestion_text(self, machine, user_event, suggestion_text):
        """
        :param machine:
        :param user_event:
        :param suggestion_text:
        :return:
        """


class WaitingForOthersState:
    def __init__(self):
        self.state_name = UserEvent.WAITING_FOR_OTHERS

    @staticmethod
    def execute(machine, user_event):
        update_user_event_state(user_event, state=UserEvent.WAITING_FOR_OTHERS)

