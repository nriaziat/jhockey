from enum import Enum, auto
from dataclasses import dataclass
from typing_extensions import Protocol
import cv2 as cv
import numpy as np
import time
from PausableTimer import PausableTimer

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
    def __init__(self, match_length: int = 10, video_feed: bool = False):
        self.match_length = match_length
        self.start_itme = None
        self.score = {Team.RED.value: 0, Team.BLUE.value: 0}
        self.timer = PausableTimer()
        self.broadcaster = None
        self.puck_tracker = None
        self.robot_tracker = None
        self._state: GameState = GameState.STOPPED
        self.video_feed = video_feed
        if self.video_feed:
            self.camera = cv.VideoCapture(1)

    @property
    def state(self) -> GameState:
        return self._state
    
    @state.setter
    def state(self, state: GameState):
        match state:
            case GameState.RUNNING:
                self.start_game()
            case GameState.STOPPED:
                self.reset()
            case GameState.PAUSED:
                self.pause()
        self._state = state

    def set_broadcaster(self, broadcaster: Broadcaster):
        self.broadcaster = broadcaster

    def set_puck_tracker(self, puck_tracker):
        self.puck_tracker = puck_tracker

    def set_robot_tracker(self, robot_tracker):
        self.robot_tracker = robot_tracker

    def start_game(self):
        '''
        Starts the game.
        '''
        if self.state == GameState.PAUSED:
            self.timer.resume()
        else:
            self.timer.start()

    def get_time_remaining(self) -> int:
        '''
        Returns the time remaining in the game.
        '''
        if not self.timer.timestarted:
            return self.match_length
        remaining = self.match_length - self.timer.get().seconds
        if remaining <= 0:
            self.reset()
            return -1
        else:
            return remaining
    def pause(self):
        '''
        Pauses the game.
        '''
        self.timer.pause()

    def reset(self):
        '''
        Resets the game state.
        '''
        self.timer = PausableTimer()
        self.start_time = None
        self.score = {Team.RED.value: 0, Team.BLUE.value: 0}

    