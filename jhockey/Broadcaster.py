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

class GameManager(Protocol):
    def seconds_remaining(self) -> float:
        """
        Returns the number of seconds remaining in the match.
        """
        ...

    @property
    def state(self) -> GameState:
        """
        Returns the state of the game.
        """
        ...


class Broadcaster:
    """
    Class to broadcast location information to each team via wifi.
    """

    def __init__(
        self,
        *,
        puck_tracker: ThreadedNode = None,
        robot_tracker: ThreadedNode = None,
        game_manager: GameManager = None,
    ):
        self.stopped = False
        self.puck_tracker = puck_tracker
        self.robot_tracker = robot_tracker
        self.game_manager = game_manager
        self.message = None

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
            puck_msg = (
                self.puck_tracker.get() if self.puck_tracker else PuckState(0, 0, False)
            )
            self.message = BroadcasterMessage(
                time=int(self.game_manager.seconds_remaining * 1e9),
                puck=puck_msg,
                robots=self.robot_tracker.get(),
                enabled=self.game_manager.state == GameState.RUNNING,
            )
            self.broadcast(self.message)

    def broadcast(self, data: dict):
        """
        Broadcasts data to each team via wifi.
        @param data: dictionary of data to broadcast
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
