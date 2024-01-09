from nicegui import ui
from typing import Protocol
from .utils import GameState, Team, RobotState
from functools import partial
import time

class GameManager(Protocol):
    @property
    def match_length_sec(self) -> int:
        ...
    
    @property
    def state(self) -> GameState:
        ...
    
    @state.setter
    def state(self, state: GameState):
        ...

    @property
    def robot_states(self) -> dict[Team, list[RobotState]]:
        ...

    @property
    def score(self) -> dict[Team, int]:
        ...
    @property
    def score_as_string(self) -> str:
        ...
    
    @property
    def seconds_remaining(self) -> int:
        ...

    def update(self):
        ...

    def reset(self):
        ...

def format_score(team: Team, score: int) -> str:
    return f"{team.name}: {score} "

class GameGUI:
    '''
    Web GUI to control the game, add score, monitor time, and start/stop gameplay.
    Optionally, monitor video feed. 

    '''
    def __init__(self, game_manager: GameManager, video_feed: bool = True):
        self.match_length_sec: int = game_manager.match_length_sec
        self.video_feed: bool = video_feed
        self.game_manager: GameManager = game_manager
        self.timer = ui.timer(0.05, self.update)

        if self.video_feed:
            self.video_feed: ui.interactive_image = ui.interactive_image().classes('w-3/4')
            with self.video_feed:
                self.score_display = ui.label(self.game_manager.score_as_string).classes('absolute-bottom text-subtitle2 text-center')
                self.score_display.bind_text_from(self.game_manager,'score_as_string')
            self.video_timer = ui.timer(interval=0.1, callback=lambda: self.video_feed.set_source(f'/video/frame?{time.time()}'))
        
        with ui.row():
            self.start_pause_button: ui.button = ui.button('Start', on_click=self.start_pause, color='green')
            self.reset_button: ui.button = ui.button('Reset', on_click=self.reset, color='red')
            self.red_score_button: ui.button = ui.button('Red Score', 
                                                         on_click=partial(self.update_score, team=Team.RED), color='red')
            self.blue_score_button: ui.button = ui.button('Blue Score',
                                                          on_click=partial(self.update_score, team=Team.BLUE), color='blue')    
            self.progress_bar = ui.circular_progress(show_value=True, size="xl", 
                                                    min=0, max=self.match_length_sec).bind_value_from(self.game_manager, 'seconds_remaining')
            self.debug_button: ui.button = ui.button('Debug Mode', on_click=self.toggle_debug, color='orange')

        self.debug: bool = False
        with ui.column().bind_visibility_from(self, 'debug'):
            columns = [
                {'name': 'robot', 'label': 'Name', 'field': 'robot', 'required': True, 'align': 'left'},
                {'name': 'x', 'label': 'x [mm]', 'field': 'x', 'sortable': True},
                {'name': 'y', 'label': 'y [mm]', 'field': 'y', 'sortable': True},
                {'name': 'theta', 'label': 'theta [deg]', 'field': 'theta', 'sortable': True},
            ]
            self.debug_table = ui.table(columns=columns, rows=[], row_key='robot')
        ui.run()

    def toggle_debug(self):
        self.debug = not self.debug

    def start_pause(self):
        if self.game_manager.state == GameState.RUNNING:
            self.set_state(GameState.PAUSED)
        else:
            self.set_state(GameState.RUNNING)

    def reset(self):
        self.set_state(GameState.STOPPED)
        self.game_manager.reset()
        self.score_display.text = f"{self.game_manager.score[Team.RED]} - {self.game_manager.score[Team.BLUE]}"

    def update(self):
        self.game_manager.update()
        if self.debug:
            rows = [
                {'robot': 'Red 1', 'x': self.game_manager.robot_states[Team.RED][0].x, 'y': self.game_manager.robot_states[Team.RED][0].y, 'theta': self.game_manager.robot_states[Team.RED][0].theta},
                {'robot': 'Red 2', 'x': self.game_manager.robot_states[Team.RED][1].x, 'y': self.game_manager.robot_states[Team.RED][1].y, 'theta': self.game_manager.robot_states[Team.RED][1].theta},
                {'robot': 'Blue 1', 'x': self.game_manager.robot_states[Team.BLUE][0].x, 'y': self.game_manager.robot_states[Team.BLUE][0].y, 'theta': self.game_manager.robot_states[Team.BLUE][0].theta},
                {'robot': 'Blue 2', 'x': self.game_manager.robot_states[Team.BLUE][1].x, 'y': self.game_manager.robot_states[Team.BLUE][1].y, 'theta': self.game_manager.robot_states[Team.BLUE][1].theta},
            ]
            self.debug_table.rows = rows
        self.update_start_button(self.game_manager.state)
                
    def update_score(self, team: Team):
        if self.game_manager.state == GameState.RUNNING:
            self.game_manager.score[team] += 1
            self.set_state(GameState.PAUSED)

    def set_state(self, state: GameState):
        self.game_manager.state = state

    def update_start_button(self, state: GameState):
        if state == GameState.STOPPED:
            self.start_pause_button.text = 'Start'
        elif state == GameState.RUNNING:
            self.start_pause_button.text = 'Pause'
        elif state == GameState.PAUSED:
            self.start_pause_button.text = 'Resume'