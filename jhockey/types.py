from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional
import logging


@dataclass
class Point:
    x: float
    y: float


@dataclass
class AruCoTag:
    id: int
    center: Point
    w: float
    h: float


class Team(Enum):
    RED = auto()
    BLUE = auto()


class GameState(Enum):
    """
    Enum to represent the state of the game.
    """

    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()

    def toggle(self):
        """
        Toggles the game state.
        """
        return GameState.PAUSED if self == GameState.RUNNING else GameState.RUNNING


@dataclass
class RobotState:
    x: int = 0  # cm
    y: int = 0  # cm
    heading: int = 0  # centirad
    found: bool = True


@dataclass
class PuckState:
    x: int  # cm
    y: int  # cm
    found: bool


@dataclass(kw_only=True)
class BroadcasterMessage:
    _max_size = 114 + 6 + 1
    time: int  # deciseconds until match end
    # Passing a Team as a key will return a list of RobotStates in order of robot ID
    robots: dict[int:RobotState]
    enabled: bool

    def to_dict(self) -> dict:
        return {
            "time": self.time,
            "robots": self.robots,
            "enabled": self.enabled,
        }

    def __str__(self) -> str:
        message = f">{self.enabled:1}{self.time:04}"  # 6 chars
        # Maximum broadcast size is 94 bytes, so we can only send 7 robots at a time
        for tag in self.robots.copy():
            message += f"{tag:02}{self.robots[tag].x:03}{self.robots[tag].y:03}{self.robots[tag].heading:03}"  # 11 chars
            if len(message) + 1 >= self._max_size:
                logging.warning(
                    "Broadcast message is too large, truncating robots list"
                )
                break
        # add end of message character
        message += "\n"
        return message


@dataclass
class GUIData:
    state: GameState
    seconds_remaining: float
    puck: Optional[PuckState]
    score: dict[Team:int]
    score_as_string: str
    robot_states: dict[int:RobotState]
    aruco_tags: list[AruCoTag]
    cam_connected: bool
    broadcast_msg: BroadcasterMessage
