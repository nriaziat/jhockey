from enum import Enum, auto
from dataclasses import dataclass
import numpy as np

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
    x: int
    y: int
    theta: int
    found: bool


@dataclass
class PuckState:
    x: int
    y: int
    found: bool


@dataclass
class GUIData:
    state: GameState
    seconds_remaining: float
    puck: PuckState
    score: dict
    score_as_string: str
    robot_states: dict[Team : list[RobotState]]
    aruco_tags: list[AruCoTag]

@dataclass(kw_only=True)
class BroadcasterMessage:
    time: int  # nsec since match start
    puck: PuckState  # optional, if implemented
    # Passing a Team as a key will return a list of RobotStates in order of robot ID
    robots: dict[Team : list[RobotState]]
