from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional


@dataclass
class AruCoTag:
    id: int
    corners: list[float]


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
        message = f">{self.time:04d}{self.enabled:1d}"  # 6 chars
        # Maximum broadcast size is 94 bytes, so we can only send 7 robots at a time
        for tag in self.robots:
            if len(message) + 1 >= self._max_size:
                break
            message += f"{tag:02d}{self.robots[tag].x:03d}{self.robots[tag].y:03d}{self.robots[tag].heading:03d}" # 11 chars
        # add end of message character
        message += "\n"
        return message