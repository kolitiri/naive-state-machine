from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from naivesm.statemachine import StateMachine


class State(Enum):
    """Defines a state for a particular entity"""


@dataclass
class Transition:
    """Defines a transition from state A to state B"""
    source: State
    destination: State
    bidirectional: bool = False


@dataclass()
class Event:
    """Defines an event produced by a state machine"""
    name: str
    source: StateMachine
    state: State
    meta: Optional[Dict[str, Any]] = None
