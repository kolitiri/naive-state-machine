import asyncio

from naivesm.models import State, Transition
from naivesm.statemachine import (
    action,
    StateMachine,
)


class SubstanceState(State):
    GAS = "GAS"
    LIQUID = "LIQUID"
    SOLID = "SOLID"
    PLASMA = "PLASMA"


class Water(StateMachine):

    transitions = [
        Transition(SubstanceState.GAS, SubstanceState.LIQUID, bidirectional=True),
        Transition(SubstanceState.LIQUID, SubstanceState.SOLID, bidirectional=True),
        Transition(SubstanceState.LIQUID, SubstanceState.PLASMA),
    ]

    @action(SubstanceState.GAS)
    def boil(self, **kwargs) -> None: ...

    @action(SubstanceState.LIQUID)
    def melt(self, **kwargs) -> None: ...

    @action(SubstanceState.SOLID)
    def freeze(self, **kwargs) -> None: ...

    @action(SubstanceState.PLASMA)
    def electrolyze(self, **kwargs) -> None: ...


class Gold(StateMachine):

    transitions = [
        Transition(SubstanceState.LIQUID, SubstanceState.SOLID, bidirectional=True),
    ]

    @action(SubstanceState.LIQUID)
    def melt(self, **kwargs) -> None: ...

    @action(SubstanceState.SOLID)
    def freeze(self, **kwargs) -> None: ...


async def run():
    water = Water(SubstanceState.LIQUID)
    gold = Gold(SubstanceState.SOLID)

    water.freeze(msg="Freezing water")
    water.melt()
    water.boil()

    gold.freeze()
    gold.melt()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
