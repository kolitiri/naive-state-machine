from naivesm.models import State


class TransitionError(Exception):
    """Raised when a transition from state A to B is not allowed."""

    def __init__(
        self, state_machine_name: str, current_state: State, target_state: State
    ) -> None:
        self.message = f"[{state_machine_name}] cannot transition from {current_state} to {target_state}"
        super().__init__(self.message)


class DuplicateStateReaction(Exception):
    """Raised when a class is implementing multiple reactions
    to the same state event.
    """

    def __init__(self, state: State, action_name: str) -> None:
        self.message = (
            f"Reaction to state {state} is already handled by function {action_name}"
        )
        super().__init__(self.message)
