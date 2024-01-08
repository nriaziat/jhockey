from enum import Enum, auto
from dataclasses import dataclass
import numpy as np

@dataclass
class FieldTag:
    id: int
    x: int
    y: int

class Team(Enum):
    RED = auto()
    BLUE = auto()

class GameState(Enum):
    '''
    Enum to represent the state of the game.
    '''
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