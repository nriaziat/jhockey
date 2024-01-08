from typing_extensions import Protocol
from .PausableTimer import PausableTimer
from .PuckTracker import PuckTracker
from .RobotTracker import RobotTracker
from .FieldHomography import FieldHomography
from .Broadcaster import Broadcaster
from .ArucoDetector import ArucoDetector
from .utils import Team, GameState, PuckState, RobotState
from typing import Optional

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
    def __init__(self, match_length_sec: int = 10,
                 broadcaster: Optional[Broadcaster] = None, 
                 puck_tracker: Optional[PuckTracker] = None,
                 robot_tracker: Optional[RobotTracker] = None, 
                 field_homography: Optional[FieldHomography] = None,
                 aruco_detector: Optional[ArucoDetector] = None):
    
        self.match_length_sec = match_length_sec
        self.start_itme = None
        self.score = {Team.RED: 0, Team.BLUE: 0}
        self.timer = PausableTimer()
        self.broadcaster: Optional[Broadcaster] = broadcaster
        self.puck_tracker: Optional[PuckTracker] = puck_tracker
        self.field_homography: Optional[FieldHomography] = field_homography
        self.robot_tracker: Optional[RobotTracker] = robot_tracker
        self.aruco_detector: Optional[ArucoDetector] = aruco_detector
        self.aruco_tags = None
        self.puck_state = PuckState(0, 0, False)
        self.robot_states = {Team.BLUE: [RobotState(0, 0, 0, False), RobotState(0, 0, 0, False)],
                             Team.RED: [RobotState(0, 0, 0, False), RobotState(0, 0, 0, False)]}
        self._state: GameState = GameState.STOPPED

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
        '''
        if not self.timer.timestarted:
            return self.match_length_sec
        remaining = self.match_length_sec - self.timer.get().seconds
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
        self.score = {Team.RED: 0, Team.BLUE: 0}

    def update_homography(self):
        '''
        Updates the field homography.
        '''
        if self.field_homography:
            self.field_homography.find_homography(self.aruco_tags)

    def update_puck(self):
        '''
        Updates the puck state.
        '''
        if self.puck_tracker:
            self.puck_state = self.puck_tracker.update()

    def update_aruco_tags(self):
        '''
        Updates the aruco tags.
        '''
        if self.aruco_detector:
            self.aruco_tags = self.aruco_detector.detect()
    
    def update_robot(self):
        '''
        Updates the robot state.
        '''
        if self.robot_tracker:
            self.robot_states = self.robot_tracker.update(self.aruco_tags, self.field_homography)

    def update(self):
        '''
        Updates the game state.
        '''
        if self.state == GameState.RUNNING:
            self.update_aruco_tags()
            self.update_homography()
            self.update_puck()
            self.update_robot()
            seconds_remaining = self.seconds_remaining
            if seconds_remaining <= 0:
                self.state = GameState.STOPPED
                seconds_remaining = 0
            if self.broadcaster is not None:
                self.broadcaster.broadcast({
                    'state': self.state,
                    'time': seconds_remaining,
                    'puck': self.puck_state,
                    Team.RED: self.robot_states[Team.RED],
                    Team.BLUE: self.robot_states[Team.BLUE]
                })
    