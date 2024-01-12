from threading import Thread
from typing import Protocol
from .utils import PuckState, RobotState, Team, BroadcasterMessage
import time


class PuckTracker(Protocol):
    def get(self) -> PuckState:
        """
        Returns the puck state.
        """
        ...


class RobotTracker(Protocol):
    def get(self) -> dict[Team, list[RobotState]]:
        """
        Returns the robot states.
        """
        ...


class Broadcaster:
    """
    Class to broadcast location information to each team via wifi.
    """

    def __init__(self, *, puck_tracker: PuckTracker = None, robot_tracker: RobotTracker = None):
        self.stopped = False
        self.puck_tracker = puck_tracker
        self.robot_tracker = robot_tracker
        self.message = None

    def start(self):
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
            puck_msg = self.puck_tracker.get() if self.puck_tracker else PuckState(0, 0, False)
            self.message = BroadcasterMessage(
                time=time.time(),
                puck=puck_msg,
                robots=self.robot_tracker.get(),
            )
            self.broadcast(self.message)

    def broadcast(self, data: dict):
        """
        Broadcasts data to each team via wifi.
        @param data: dictionary of data to broadcast
        """
        pass

    def get(self) -> dict:
        """
        Returns the message to be broadcasted.
        """
        return self.message

    def stop(self):
        """
        Stops the broadcaster.
        """
        self.stopped = True
