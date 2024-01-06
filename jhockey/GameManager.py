from enum import Enum, auto
from dataclasses import dataclass
from typing_extensions import Protocol

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

class Broadcaster(Protocol):

    def broadcast(self, data: dict):
        '''
        Broadcasts data to each team via wifi.
        '''
        ...

class GameManager:
    '''
    Class to manage score, time, and other game information.
    Arbitrates communication between the game controller and the teams.
    '''
    def __init__(self):
        self.score = {'red': 0, 'blue': 0}
        self.time = 0
        self.game_state: GameState = GameState.STOPPED
        self.game_gui = None
        self.broadcaster = None
        self.red_robot_state = RobotState(0, 0, 0, False)
        self.blue_robot_state = RobotState(0, 0, 0, False)
        self.puck_state = RobotState(0, 0, False)
        self.puck_tracker = None
        self.robot_tracker = None
