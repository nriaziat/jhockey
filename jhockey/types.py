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


@dataclass(kw_only=True)
class BroadcasterMessage:
    time_dsec: int  # deciseconds until match end
    # Passing a Team as a key will return a list of RobotStates in order of robot ID
    robots: dict[int:RobotState]
    enabled: bool
    _max_bytes = 114

    def to_dict(self) -> dict:
        return {
            "time": self.time_dsec,
            "robots": self.robots,
            "enabled": self.enabled,
        }

    def __str__(self) -> str:
        message = f">{self.enabled:1}{self.time_dsec:04}" 
        for tag in self.robots.copy():
            message += f"{ascii_uppercase[tag]}{self.robots[tag].x_cm:03}{self.robots[tag].y_cm:03}"  
            if len(message) > self._max_bytes:
                logging.warning(
                    "Broadcast message is too large, truncating robots list"
                )
                break
        # add end of message character
        cheksum = sum([ord(c) for c in message]) % 64
        message += f"{cheksum:02};"
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