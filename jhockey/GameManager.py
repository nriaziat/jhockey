from typing_extensions import Protocol
from .types import (
    Team,
    GUIData,
    PuckState,
    RobotState,
    AruCoTag,
    GameState,
    BroadcasterMessage,
)
from typing import Optional
import threading
from typing import Any
from datetime import datetime


class PausableTimer(Protocol):
    def start(self):
        """
        Starts the timer.
        """
        ...

    def pause(self):
        """
        Pauses the timer.
        """
        ...

    def resume(self):
        """
        Resumes the timer.
        """
        ...

    def get(self) -> datetime:
        """
        Returns the time elapsed.
        """
        ...

    def reset(self):
        """
        Resets the timer.
        """
        ...

    @property
    def timestarted(self) -> bool:
        """
        Returns whether the timer has started.
        """
        ...


class ThreadedNode(Protocol):
    def get(self) -> Any:
        ...

    def set(self, data: Any) -> None:
        ...

class ArucoDetector(Protocol):
    def get(self) -> list[AruCoTag]:
        ...

    @property
    def connected(self) -> bool:
        ...

class Broadcaster(Protocol):
    def set_message(self, message: BroadcasterMessage) -> None:
        """
        Sets the message to be broadcast.
        """
        ...


class FieldHomography(Protocol):
    def find_homography(self, field_tags: list[AruCoTag]) -> None:
        """
        Updates the field homography.
        """
        ...


class GUI(Protocol):
    def create_ui(self, match_length_sec: int) -> None:
        ...

    def update(self, data: dict) -> None:
        """
        Updates the GUI.
        """
        ...


class GameManager:
    """
    Class to manage score, time, and other game information.
    Arbitrates communication between the game controller and the teams.
    """

    def __init__(
        self,
        *,
        match_length_sec: int = 10,
        broadcaster: ThreadedNode = None,
        puck_tracker: ThreadedNode = None,
        robot_tracker: ThreadedNode = None,
        field_homography: FieldHomography = None,
        aruco_detector: ArucoDetector = None,
        gui: Optional[GUI] = None,
        timer: PausableTimer = None,
    ):
        """
        Parameters
        ----------
        match_length_sec : int, optional
            The length of the match in seconds, by default 10
        broadcaster : ThreadedNode
            The broadcaster node.
        puck_tracker : ThreadedNode
            The puck tracker node.
        robot_tracker : ThreadedNode
            The robot tracker node.
        field_homography : FieldHomography
            The field homography object.
        aruco_detector : ThreadedNode
            The ArUco detector node.
        gui : GUI, optional
            The GUI object, by default None
        timer : PausableTimer
            The timer object.
        """
        self.match_length_sec = match_length_sec
        self.start_time = None
        self.score = {Team.RED: 0, Team.BLUE: 0}
        self.timer = timer
        self.broadcaster: Optional[Broadcaster] = broadcaster
        self.puck_tracker: Optional[ThreadedNode] = puck_tracker
        self.puck_state: Optional[PuckState] = None
        self.field_homography: Optional[FieldHomography] = field_homography
        self.robot_tracker: Optional[ThreadedNode] = robot_tracker
        self.robot_states: Optional[dict[Team : list[RobotState]] | dict[int, RobotState]] = None
        self.aruco_detector: Optional[ThreadedNode] = aruco_detector
        self.gui: Optional[GUI] = gui
        self.gui.create_ui(self.match_length_sec)
        self._state: GameState = GameState.STOPPED
        self.lock = threading.Lock()

    def start(self):
        """
        Starts the thread.
        """
        t = threading.Thread(target=self.update, name="Game Manager")
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
        """
        Returns the score as a string.
        """
        return f"Red: {self.score[Team.RED]}, Blue: {self.score[Team.BLUE]}"

    def start_game(self):
        """
        Starts the game.
        """
        if self.state == GameState.PAUSED:
            self.timer.resume()
        else:
            self.score = {Team.RED: 0, Team.BLUE: 0}
            self.timer.start()

    @property
    def seconds_remaining(self) -> float:
        """
        Returns the time remaining in the game.
        If remaining time is negative, resets the game.
        """
        if not self.timer.timestarted:
            return self.match_length_sec
        remaining = self.match_length_sec - self.timer.get().seconds
        return remaining if remaining > 0 else 0

    def pause(self):
        """
        Pauses the game.
        """
        self.timer.pause()

    def reset(self):
        """
        Resets the game state.
        """
        self.timer.reset()
        self.start_time = None

    def update(self):
        """
        Updates the game state.
        """
        while True:
            self.aruco_detector.detect()
            aruco_tags = self.aruco_detector.get()
            self.field_homography.find_homography(aruco_tags)
            H = self.field_homography.H
            self.robot_tracker.set(aruco_tags, H)
            self.puck_state = None
            if self.puck_tracker is not None:
                self.puck_state = self.puck_tracker.get()
            self.robot_states = self.robot_tracker.get()

            if self.seconds_remaining <= 0:
                self.state = GameState.STOPPED

            if self.broadcaster is not None:
                time_left_decisecond = int(self.timer.get().total_seconds * 1e1) if self.timer.timestarted else self.match_length_sec * 1e1
                self.broadcaster.set_message(
                    BroadcasterMessage(
                        time=time_left_decisecond,
                        robots=self.robot_states,
                        puck=self.puck_state,
                        enabled=self.state == GameState.RUNNING,
                    )
                )

            if self.gui is not None:
                self.update_gui(aruco_tags)
        
    def update_gui(self, aruco_tags: list[AruCoTag]):
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
        send_data = GUIData(
            state=self.state,
            seconds_remaining=self.seconds_remaining,
            puck=self.puck_state,
            score=self.score,
            score_as_string=self.score_as_string,
            robot_states=self.robot_states,
            aruco_tags=aruco_tags,
            cam_connected=self.aruco_detector.connected,
        )
        self.gui.update(send_data)  # used to thread lock this, dont think we need to anymore
