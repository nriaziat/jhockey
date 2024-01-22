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
    robot_states: dict[Team : list[RobotState]] | dict[int:RobotState]
    aruco_tags: list[AruCoTag]
    cam_connected: bool


@dataclass(kw_only=True)
class BroadcasterMessage:
    time: int  # usec since match start
    puck: Optional[PuckState]  # optional, if implemented
    # Passing a Team as a key will return a list of RobotStates in order of robot ID
    robots: dict[Team : list[RobotState]] | dict[int:RobotState]
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
        # return f">{self.time:06d},
        #         {self.enabled:1d},
        #         AA,{self.robots[Team.RED][0].x:04d},{self.robots[Team.RED][0].y:04d}, {self.robots[Team.RED][0].heading:04d},
        #         AB,{self.robots[Team.RED][1].x:04d},{self.robots[Team.RED][1].y:04d}, {self.robots[Team.RED][1].heading:04d},
        #         BA,{self.robots[Team.BLUE][0].x:04d},{self.robots[Team.BLUE][0].y:04d}, {self.robots[Team.BLUE][0].heading:04d},
        #         BB,{self.robots[Team.BLUE][1].xL:04d},{self.robots[Team.BLUE][1].y:04d}, {self.robots[Team.BLUE][1].heading:04d}"
        message = f">{self.time:06d},{self.enabled:1d}"
        for tag in self.robots:
            message += f",{tag:02d},{self.robots[tag].x:04d},{self.robots[tag].y:04d},{self.robots[tag].heading:04d}"
