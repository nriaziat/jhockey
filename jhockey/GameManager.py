from typing_extensions import Protocol
import cv2 as cv
from PausableTimer import PausableTimer
from PuckTracker import PuckTracker
from RobotTracker import RobotTracker
from FieldHomography import FieldHomography
from Broadcaster import Broadcaster
from ArucoDetector import ArucoDetector
from utils import Team, GameState, PuckState, RobotState
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
    def __init__(self, match_length: int = 10, video_feed: bool = False):
        self.match_length = match_length
        self.start_itme = None
        self.score = {Team.RED: 0, Team.BLUE: 0}
        self.timer = PausableTimer()
        self.broadcaster: Optional[Broadcaster] = None
        self.puck_tracker: Optional[PuckTracker] = None
        self.field_homography: Optional[FieldHomography] = None
        self.robot_tracker: Optional[RobotTracker] = None
        self.aruco_tags = None
        self.aruco_detector = None
        self.puck_state = PuckState(0, 0, False)
        self.robot_states = {Team.BLUE: [RobotState(0, 0, 0, False), RobotState(0, 0, 0, False)],
                             Team.RED: [RobotState(0, 0, 0, False), RobotState(0, 0, 0, False)]}
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

    def set_puck_tracker(self, puck_tracker: PuckTracker):
        self.puck_tracker = puck_tracker

    def set_robot_tracker(self, robot_tracker: RobotTracker):
        self.robot_tracker = robot_tracker

    def set_field_homography(self, field_homography: FieldHomography):
        self.field_homography = field_homography

    def set_aruco_detector(self, aruco_detector: ArucoDetector):
        self.aruco_detector = aruco_detector

    def start_game(self):
        '''
        Starts the game.
        '''
        if self.state == GameState.PAUSED:
            self.timer.resume()
        else:
            self.timer.start()

    @property
    def seconds_remaining(self) -> int:
        '''
        Returns the time remaining in the game.
        '''
        if not self.timer.timestarted:
            return self.match_length
        remaining = self.match_length - self.timer.get().seconds
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
            self.broadcaster.broadcast({
                'state': self.state,
                'time': seconds_remaining,
                'puck': self.puck_state,
                Team.RED: self.robot_states[Team.RED],
                Team.BLUE: self.robot_states[Team.BLUE]
            })

    