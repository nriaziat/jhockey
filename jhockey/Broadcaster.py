from __future__ import annotations
from threading import Thread
from typing import Protocol
from .types import PuckState, RobotState, Team, BroadcasterMessage, GameState

class ThreadedNode(Protocol):
    def get(self) -> PuckState | dict[Team, list[RobotState]]:
        """
        Returns the puck state.
        """
        ...
class PausableTimer(Protocol):
    def start(self):
        """
        Starts the timer.
        """
        ...

    def pause(self):
        """
        Pauses the timer.
        """
        ...

    def resume(self):
        """
        Resumes the timer.
        """
        ...

    def get(self) -> float:
        """
        Returns the time elapsed.
        """
        ...

    def reset(self):
        """
        Resets the timer.
        """
        ...

    @property
    def timestarted(self) -> bool:
        """
        Returns whether the timer has started.
        """
        ...


class Broadcaster:
    """
    Class to broadcast location information to each team via wifi.
    """

    def __init__(
        self):
        self.stopped = False
        self.message = None
        self.game_state = GameState.STOPPED

    def start(self) -> Broadcaster:
        """
        Starts the broadcaster.
        """
        t = Thread(target=self.run, name="Broadcaster")
        t.daemon = True
        t.start()
        return self

    def run(self):
        """
        Runs the broadcaster.
        """
        while True:
            if self.stopped:
                return
            if self.message is None:
                continue
            self.broadcast(self.message)

    def broadcast(self, msg: BroadcasterMessage):
        """
        Broadcasts data to robots.
        @param data: BroadcasterMessage to broadcast
        """
        pass

    def get(self) -> BroadcasterMessage:
        """
        Returns the message to be broadcasted.
        """
        return self.message

    def stop(self):
        """
        Stops the broadcaster.
        """
        self.stopped = True

    def set_message(self, message: BroadcasterMessage):
        """
        Sets the message to be broadcast.
        """
        self.message = message
