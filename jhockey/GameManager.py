from enum import Enum, auto
from dataclasses import dataclass
from typing_extensions import Protocol
import cv2 as cv
import numpy as np

class Team(Enum):
    RED = 'red'
    BLUE = 'blue'

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
    def __init__(self, start_time: int = 10, video_feed: bool = False):
        self.score = {Team.RED.value: 0, Team.BLUE.value: 0}
        self.time = start_time
        self.broadcaster = None
        self.puck_tracker = None
        self.robot_tracker = None
        self.state: GameState = GameState.STOPPED
        if video_feed:
            self.camera = cv.VideoCapture(1)

    def get_time_remaining(self) -> int:
        '''
        Returns the time remaining in the game.
        '''
        return self.time
    