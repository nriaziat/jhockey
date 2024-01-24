from __future__ import annotations
from threading import Thread
from typing import Protocol
from .types import PuckState, RobotState, Team, BroadcasterMessage, GameState
from digi.xbee.devices import XBeeDevice

class ThreadedNode(Protocol):
    def get(self) -> PuckState | dict[Team, list[RobotState]] | dict[int, RobotState]:
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


class XBeeBroadcaster:
    """
    Class to broadcast location information to each team via XBee protocol.
    """

    def __init__(self, port="/dev/ttyUSB0"):
        self.xbee = XBeeDevice(port, 115200)
        self.xbee.open()
        self.stopped = False
        self.message = None
        self.game_state = GameState.STOPPED

    def start(self) -> XBeeBroadcaster:
        """
        Starts the broadcaster.
        """
        t = Thread(target=self.run, name="XBee Broadcaster")
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
        self.xbee.send_data_broadcast(str(msg))

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
