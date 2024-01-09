from typing_extensions import Protocol
from .utils import Team, GameState, PuckState, RobotState
from typing import Optional
import numpy as np
import cv2 as cv
import threading

class PausableTimer(Protocol):
        def start(self):
            '''
            Starts the timer.
            '''
            ...
    
        def pause(self):
            '''
            Pauses the timer.
            '''
            ...
    
        def resume(self):
            '''
            Resumes the timer.
            '''
            ...
    
        def get(self) -> float:
            '''
            Returns the time elapsed.
            '''
            ...
        
        def reset(self):
            '''
            Resets the timer.
            '''
            ...
    
        @property
        def timestarted(self) -> bool:
            '''
            Returns whether the timer has started.
            '''
            ...

class ThreadedNode(Protocol):
    def get(self):
        ...

class FieldHomography(Protocol):
    def find_homography(self, field_tags: list) -> np.ndarray:
        '''
        Updates the field homography.
        '''
        ...

class GUI(Protocol):
    def create_ui(self, match_length_sec: int):
        ...
    def update(self, data: dict):
        '''
        Updates the GUI.
        '''
        ...

class GameManager:
    '''
    Class to manage score, time, and other game information.
    Arbitrates communication between the game controller and the teams.
    '''
    def __init__(self, *, match_length_sec: int = 10,
                 broadcaster: Optional[ThreadedNode] = None, 
                 puck_tracker: Optional[ThreadedNode] = None,
                 robot_tracker: Optional[ThreadedNode] = None, 
                 field_homography: Optional[FieldHomography] = None,
                 aruco_detector: Optional[ThreadedNode] = None, 
                 gui: Optional[GUI] = None,
                 timer: PausableTimer = None):
    
        self.match_length_sec = match_length_sec
        self.start_time = None
        self.score = {Team.RED: 0, Team.BLUE: 0}
        self.timer = timer
        self.broadcaster: Optional[ThreadedNode] = broadcaster
        self.puck_tracker: Optional[ThreadedNode] = puck_tracker
        self.field_homography: Optional[FieldHomography] = field_homography
        self.robot_tracker: Optional[ThreadedNode] = robot_tracker
        self.aruco_detector: Optional[ThreadedNode] = aruco_detector
        self.gui: Optional[GUI] = gui
        self.gui.create_ui(self.match_length_sec)
        self._state: GameState = GameState.STOPPED
        self.lock = threading.Lock()

    def start(self):
        '''
        Starts the thread.
        '''
        t = threading.Thread(target=self.update)
        t.daemon = True
        t.start()
        return self

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

    @property
    def score_as_string(self) -> str:  
        '''
        Returns the score as a string.
        '''
        return f"Red: {self.score[Team.RED]}, Blue: {self.score[Team.BLUE]}"

    def start_game(self):
        '''
        Starts the game.
        '''
        if self.state == GameState.PAUSED:
            self.timer.resume()
        else:
            self.timer.start()

    @property
    def seconds_remaining(self) -> float:
        '''
        Returns the time remaining in the game.
        If remaining time is negative, resets the game.
        '''
        if not self.timer.timestarted:
            return self.match_length_sec
        remaining = self.match_length_sec - self.timer.get().seconds
        if remaining <= 0:
            self.reset()
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
        self.timer.reset()
        self.start_time = None
        self.score = {Team.RED: 0, Team.BLUE: 0}

    def update_homography(self):
        '''
        Updates the field homography.
        '''
        return
        self.field_homography.find_homography(self.aruco_tags)

    def update_puck(self):
        '''
        Updates the puck state.
        '''
        with self.lock:
            self.puck_state = self.puck_tracker.get()

    def update_aruco_tags(self):
        '''
        Updates the aruco tags.
        '''
        with self.lock:
            self.aruco_tags = self.aruco_detector.get()
    
    def update_robot(self):
        '''
        Updates the robot state.
        '''
        with self.lock:
            self.robot_states = self.robot_tracker.get()

    def update(self):
        '''
        Updates the game state.
        '''
        while True:
            if self.gui is not None:
                add_score = self.gui.add_score 
                if add_score is not None:
                    self.score[add_score] += 1 
                reset_state = self.gui.reset_state
                if reset_state:
                    self.state = GameState.STOPPED
                else: 
                    toggle_state = self.gui.toggle_state
                    if toggle_state:
                        if self.state == GameState.RUNNING:
                            self.state = GameState.PAUSED
                        else:
                            self.state = GameState.RUNNING
                robot_states = self.robot_tracker.get()
                puck_state = self.puck_tracker.get()
                with self.lock:
                    self.gui.update({
                        'state': self.state,
                        'seconds_remaining': self.seconds_remaining,
                        'puck': puck_state,
                        'score': self.score,
                        'score_as_string': self.score_as_string,
                        'robot_states': robot_states
                    })

            if self.state == GameState.RUNNING:
                self.update_aruco_tags()
                self.update_homography()
                self.update_puck()
                self.update_robot()
                seconds_remaining = self.seconds_remaining
                if seconds_remaining <= 0:
                    self.state = GameState.STOPPED
                    seconds_remaining = 0