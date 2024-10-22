# naive-state-machine
1. [Description](#description)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Usage](#usage)
    * [Actions](#actions)
    * [Reactions](#reactions)
    * [Broadcasting and Subscribing](#broadcast-subscribe)
5. [Notes](#notes)

# Description <a name="description"></a>
There are a number of state machine libraries in python and I believe the most popular one is the [python-statemachine](https://python-statemachine.readthedocs.io/en/latest/) by Fernando Macedo (fgmacedo). It is in active development and has a decent amount of stars and a lot of contributors.

However, I wanted to roll out my own version in an attempt to experiment and see if I can create something more intuitive.

This is a naive implementation of a state machine.

It allows you to create custom state machines which can also interact with each other through published events.

# Requirements <a name="requirements"></a>
This version was developed using Python 3.11 but you can certainly adjust it to work with earlier python versions.

It is based one standard python libraries and has no external dependencies (other than pytest & black for for development purposes).

# Installation <a name="installation"></a>
This project is using [poetry](https://python-poetry.org/) for dependency management.

You can install the virtual environment as such.
```bash
poetry install
```

# Usage <a name="usage"></a>
You can experiment with the existing examples or start with a fresh module.

To define a new state machine entity, start by creating a `State` enum that describes the states of the machine.

```python
class TrafficLightState(State):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"
```

Then, create the actual state machine class.

```python
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
```

Within the state machine class, define the Transitions that are expected.

For example, a traffic light can transition from Green to Yellow, from Yellow to Red and from Red to Green.

If a Transition works both ways, you can set the `bidirectional` argument to `True`.

## Actions <a name="actions"></a>
Within a state machine class, you can have `@action` decorated functions.

Actions are essentially events that trigger a transition to a target state.

For example, calling the `green()` function will trigger an event that, if allowed, will transition the state of the traffic light to Green.

Actions can be broadcasted to other state machines (if any has subscribed) by setting the `bradcast` argument to `True`.

## Reactions <a name="reactions"></a>
Within a state machine class, you can also have `@reaction` decorated functions.

Reactions are events that are triggered when there is a transition to the state of an external state machine.

For example, if we had a cyclist state machine that has subscribed to our traffic light, we can get the cyclist react when the traffic light goes Red.

We can do that by defining an `on_red_light` reaction like below:
```python
@reaction(TrafficLightState.RED)
def on_red_light(self, event: Event) -> None:
    self.stop()
```

## Broadcasting and Subscribing <a name="broadcast-subscribe"></a>
Any state machine can choose to broadcast its actions to all the external machines that have subscribed to it.

The same way, any state machine can choose to subscribe to any number of external state machines.

Broadcasting can be achieved by setting the `broadcast` argument to `True` in the `@action` decorator.

Subscribing can be achieved by calling the `subscribe()` function with a list of state machine objects that we want to subscribe to.

Take a look at the examples provided for more details.

# Notes <a name="notes"></a>
This is a beta version and is most likely buggy at the moment.

For a few more details, you can take a look at an article I wrote here: [A naive State Machine](https://kolitiri.github.io/blogging-time/posts/naive-state-machine/)

# License
This project is licensed under the terms of the MIT license.

# Authors
Christos Liontos
