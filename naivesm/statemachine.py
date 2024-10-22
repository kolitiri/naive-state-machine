from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from naivesm.exceptions import DuplicateStateReaction, TransitionError
from naivesm.models import State, Event, Transition


def action(
    state: State,
    broadcast: bool = False,
    when: Optional[Set[State]] = None,
    unless: Optional[Set[State]] = None,
) -> Callable:
    """Decorator indicating that a function is an action of the
    state machine object.
    """

    def decorator(function):
        @wraps(function)
        def wrapper(self, **kwargs) -> None:

            states = set(list(self.publishers.values()) + [self.state])

            # If none of the when conditions are satisfied, do not process
            if when and not when.intersection(states):
                print(f"[{self}] cannot {function.__name__} unless {when}")
                return

            # If any of the unless conditions are satisfied, do not process
            if unless and unless.intersection(states):
                print(f"[{self}] cannot {function.__name__} when {unless}")
                return

            function(self, **kwargs)

            self.process_event(
                Event(name=function.__name__, source=self, state=state, meta=kwargs)
            )

        setattr(wrapper, "__broadcast__", broadcast)
        setattr(wrapper, "__transitions_to__", state)
        setattr(wrapper, "__is_action_function__", True)
        return wrapper

    return decorator


def reaction(
    state: State, when: Optional[Set[State]] = None, unless: Optional[Set[State]] = None
) -> Callable:
    """Decorator indicating that a function is a reaction to a
    change in the state of an external state machine object.
    """

    def decorator(function):
        @wraps(function)
        def wrapper(self, event: Event) -> None:

            states = set(list(self.publishers.values()) + [self.state])

            # If none of the when conditions are satisfied, do not process
            if when and not when.intersection(states):
                print(f"[{self}] cannot react {function.__name__} unless {when}")
                return

            # If any of the unless conditions are satisfied, do not process
            if unless and unless.intersection(states):
                print(f"[{self}] cannot react {function.__name__} when {unless}")
                return

            function(self, event)

        setattr(wrapper, "__reacts_to__", state)
        setattr(wrapper, "__is_reaction_function__", True)
        return wrapper

    return decorator


class StateMachineMeta(type):
    """Metaclass used as a base to create StateMachine classes.

    It stores functions that are decorated as actions or reactions.
    """

    def __new__(
        mcs: type, name: str, bases: Tuple[Any], namespace: Dict[Any, Any], /, **kwargs
    ) -> "StateMachineMeta":
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        cls.broadcast_events = []
        cls.reactions_to_state = {}
        for name, value in namespace.items():
            action_name = name
            if getattr(value, "__is_action_function__", False):
                state = value.__transitions_to__

                if getattr(value, "__broadcast__", False):
                    cls.broadcast_events.append(action_name)

            if getattr(value, "__is_reaction_function__", False):
                state = value.__reacts_to__
                if state in cls.reactions_to_state:
                    raise DuplicateStateReaction(state, action_name)

                cls.reactions_to_state[state] = value

        return cls


class StateMachine(metaclass=StateMachineMeta):
    """State machine class used to define state machine objects"""

    transitions: List[Transition]
    broadcast_events: List[str]
    reactions_to_state: Dict[State, Callable]

    def __init__(self, initial_state: State) -> None:
        self.events = []
        self.state = initial_state

        self.transitions_map = {}
        self.consumers = set()
        self.publishers = {}
        self.name = self.__class__.__name__.lower()

        print(f"[{self.name}] starting in state {self.state}")

        for transition in self.transitions:
            self.transitions_map.setdefault(transition.source, [])
            self.transitions_map[transition.source].append(transition.destination)
            if transition.bidirectional:
                self.transitions_map.setdefault(transition.destination, [])
                self.transitions_map[transition.destination].append(transition.source)

    def register(self, consumers: List["StateMachine"]) -> None:
        """Registers a list of external state machine objects to publish event to"""
        for consumer in consumers:
            print(f"[{self.name}] registering consumer [{consumer}]")
            self.consumers.add(consumer)

    def subscribe(self, publishers: List["StateMachine"]) -> None:
        """Subscribes to a list of external state machine objects to consume events from"""
        for publisher in publishers:
            self.publishers[publisher] = publisher.state
            publisher.register([self])

    def publish_event(self, event: Event) -> None:
        """Publishes an event to all registered external state machine objects"""
        for consumer in self.consumers:
            print(f"[{self.name}] publishing {event.name} to [{consumer}]")
            consumer.process_event(event)

    def process_event(self, event: Event) -> None:
        """Processes either an internal or external event"""
        self.events.append(event)

        if event.source == self:
            print(f"[{self.name}] processing event {event.name}")
            self._process_internal_event(event)
        else:
            print(f"[{self.name}] processing event {event.name} from [{event.source}]")
            self._process_external_event(event)

    def _process_internal_event(self, event: Event) -> None:
        """Processes an internal event produces by an action function"""
        target_state = event.state
        if self.state == target_state:
            return

        if target_state in self.transitions_map.get(self.state, []):
            print(f"[{self.name}] transitioning from {self.state} to {target_state}")
            self.state = target_state

            if event.name in self.broadcast_events:
                self.publish_event(Event(event.name, self, self.state, meta=event.meta))
        else:
            raise TransitionError(self.name, self.state, target_state)

    def _process_external_event(self, event: Event) -> None:
        """Processes an external event produced by one of the subscribed state machine objects"""
        self.publishers[event.source] = event.state

        reaction_fn = self.reactions_to_state.get(event.state)
        if reaction_fn:
            reaction_fn(self, event)

    def __repr__(self) -> str:
        return self.name
