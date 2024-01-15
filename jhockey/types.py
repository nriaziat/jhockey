from enum import Enum, auto
from dataclasses import dataclass
import numpy as np
from typing import Optional

@dataclass
class AruCoTag:
    id: int
    corners: list[np.ndarray]


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
    y: int = 0 # mm  
    heading: int = 0 # millirad
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
    score: dict[Team : int]
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
