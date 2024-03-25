from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional
from string import ascii_uppercase
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


@dataclass
class GUIData:
    state: GameState
    seconds_remaining: float
    puck: Optional[PuckState]
    score: dict[Team:int]
    score_as_string: str
    robot_states: dict[Team : list[RobotState]] | dict[int:RobotState]
    aruco_tags: list[AruCoTag]
    cam_connected: bool


@dataclass(kw_only=True)
class BroadcasterMessage:
    _max_size = 7
    time: int  # deciseconds until match end
    # Passing a Team as a key will return a list of RobotStates in order of robot ID
    robots: dict[Team : list[RobotState]] | dict[int:RobotState]
    enabled: bool

    def to_dict(self) -> dict:
        return {
            "time": self.time,
            "robots": self.robots,
            "enabled": self.enabled,
        }

    def __str__(self) -> str:
        message = f">{self.enabled:1}{self.time_dsec:04}"  # 6 chars
        # Maximum broadcast size is 94 bytes, so we can only send 11 robots at a time
        for tag in self.robots.copy():
            message += f"{ascii_uppercase[tag]}{self.robots[tag].x_cm:03}{self.robots[tag].y_cm:03}"  # 7 chars
            if len(message) + 1 >= self._max_bytes:
                logging.warning(
                    "Broadcast message is too large, truncating robots list"
                )
                break
        # add end of message character
        cheksum = sum([ord(c) for c in message]) % 64
        message += f"{cheksum:02};"
        return message