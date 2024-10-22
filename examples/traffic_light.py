import asyncio

from naivesm.models import State, Event, Transition
from naivesm.statemachine import (
    action,
    reaction,
    StateMachine,
)


class TrafficLightState(State):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


class CyclistState(State):
    CYCLING = "CYCLING"
    STOPPED = "STOPPED"


class PoliceCarState(State):
    ROLLING = "ROLLING"
    STOPPED = "STOPPED"
    CHASING = "CHASING"


class TrafficLight(StateMachine):

    transitions = [
        Transition(TrafficLightState.GREEN, TrafficLightState.YELLOW),
        Transition(TrafficLightState.YELLOW, TrafficLightState.RED),
        Transition(TrafficLightState.RED, TrafficLightState.GREEN),
    ]

    @action(TrafficLightState.GREEN, broadcast=True)
    def green(self, **kwargs) -> None: ...

    @action(TrafficLightState.YELLOW, broadcast=True)
    def yellow(self, **kwargs) -> None: ...

    @action(TrafficLightState.RED, broadcast=True)
    def red(self, **kwargs) -> None: ...


class Cyclist(StateMachine):

    transitions = [
        Transition(CyclistState.STOPPED, CyclistState.CYCLING),
        Transition(CyclistState.CYCLING, CyclistState.STOPPED),
    ]

    @action(
        CyclistState.CYCLING,
        when={TrafficLightState.GREEN, TrafficLightState.YELLOW},
        unless={PoliceCarState.CHASING},
    )
    def cycle_fast(self, **kwargs) -> None: ...

    @action(
        CyclistState.CYCLING,
        when={TrafficLightState.GREEN},
        unless={PoliceCarState.CHASING},
    )
    def cycle_slow(self, **kwargs) -> None: ...

    @action(CyclistState.STOPPED)
    def stop(self, **kwargs) -> None: ...

    @reaction(TrafficLightState.GREEN)
    def on_green_light(self, event: Event) -> None:
        self.cycle_slow()

    @reaction(TrafficLightState.RED)
    def on_red_light(self, event: Event) -> None:
        self.stop()

    @reaction(PoliceCarState.CHASING)
    def on_being_chased(self, event: Event) -> None:
        self.stop()


class PoliceCar(StateMachine):

    transitions = [
        Transition(PoliceCarState.ROLLING, PoliceCarState.STOPPED, bidirectional=True),
        Transition(PoliceCarState.ROLLING, PoliceCarState.CHASING, bidirectional=True),
        Transition(PoliceCarState.STOPPED, PoliceCarState.CHASING, bidirectional=True),
    ]

    @action(PoliceCarState.CHASING, broadcast=True)
    def chase(self, **kwargs) -> None: ...

    @action(PoliceCarState.ROLLING, broadcast=True)
    def roll(self, **kwargs) -> None: ...

    @action(PoliceCarState.STOPPED)
    def stop(self, **kwargs) -> None: ...

    @reaction(TrafficLightState.GREEN, unless={PoliceCarState.CHASING})
    def on_green_light(self, event: Event) -> None:
        self.roll()

    @reaction(TrafficLightState.RED, unless={PoliceCarState.CHASING})
    def on_red_light(self, event: Event) -> None:
        self.stop()


async def run():
    traffic_light = TrafficLight(TrafficLightState.YELLOW)
    cyclist = Cyclist(CyclistState.CYCLING)
    police_car = PoliceCar(PoliceCarState.ROLLING)

    cyclist.subscribe([traffic_light])
    police_car.subscribe([traffic_light])
    police_car.register([cyclist])

    traffic_light.red()
    traffic_light.green()
    traffic_light.yellow()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
