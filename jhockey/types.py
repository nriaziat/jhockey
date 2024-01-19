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
    x: int = 0  # mm
    y: int = 0  # mm
    heading: int = 0  # millirad
    found: bool = True


@dataclass
class PuckState:
    x: int  # mm
    y: int  # mm
    found: bool


@dataclass
class GUIData:
    state: GameState
    seconds_remaining: float
    puck: Optional[PuckState]
    score: dict[Team:int]
    score_as_string: str
    robot_states: dict[Team : list[RobotState]]
    aruco_tags: list[AruCoTag]
    cam_connected: bool


@dataclass(kw_only=True)
class BroadcasterMessage:
    time: int  # usec since match start
    puck: Optional[PuckState]  # optional, if implemented
    # Passing a Team as a key will return a list of RobotStates in order of robot ID
    robots: dict[Team : list[RobotState]]
    enabled: bool

    def to_dict(self) -> dict:
        if self.puck is not None:
            return {
                "time": self.time,
                "puck": self.puck,
                "robots": self.robots,
                "enabled": self.enabled,
            }
        else:
            return {
                "time": self.time,
                "robots": self.robots,
                "enabled": self.enabled,
            }

    def __str__(self) -> str:
        if self.puck is not None:
            return f"{self.time},{self.puck.x},{self.puck.y},{self.robots[Team.RED][0].x},{self.robots[Team.RED][0].y},{self.robots[Team.BLUE][0].x},{self.robots[Team.BLUE][0].y},{self.enabled}"
        else:
            return f"{self.time},{self.robots[Team.RED][0].x},{self.robots[Team.RED][0].y},{self.robots[Team.BLUE][0].x},{self.robots[Team.BLUE][0].y},{self.enabled}"
