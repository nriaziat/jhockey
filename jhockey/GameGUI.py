from nicegui import ui
from .GameManager import GameManager
from .utils import GameState, Team
from functools import partial
import time

class GameGUI:
    '''
    Web GUI to control the game, add score, monitor time, and start/stop gameplay.
    Optionally, monitor video feed. 
    '''
    def __init__(self, game_manager: GameManager, video_feed: bool = True):
        self.match_length_sec: int = game_manager.match_length_sec
        self.video_feed: bool = video_feed
        self.game_manager: GameManager = game_manager

        with ui.row():
            self.start_pause_button: ui.button = ui.button('Start', on_click=self.start_pause, color='green')
            self.reset_button: ui.button = ui.button('Reset', on_click=self.reset, color='red')

        self.timer = ui.timer(0.1, self.update)
        self.progress_bar = ui.circular_progress(show_value=True, size="xl", min=0, max=self.match_length_sec).bind_value_from(self.game_manager, 'seconds_remaining')

        self.score_display: ui.label = ui.label('0 - 0')
        with ui.row():
            self.red_score_button: ui.button = ui.button('Red Score', on_click=partial(self.update_score, team=Team.RED), color='red')
            self.blue_score_button: ui.button = ui.button('Blue Score', on_click=partial(self.update_score, team=Team.BLUE), color='blue')

        if self.video_feed:
            self.video_feed: ui.interactive_image = ui.interactive_image().classes('w-full h-full')
            self.video_timer = ui.timer(interval=0.1, callback=lambda: self.video_feed.set_source(f'/video/frame?{time.time()}'))
        
        self.debug_button: ui.button = ui.button('Debug Mode', on_click=self.toggle_debug, color='yellow')
        self.debug: bool = False
        with ui.column().bind_visibility_from(self, 'debug'):
            self.debug_label: ui.label = ui.label('Debug Mode')
            self.robot1_label: ui.label = ui.label('Robot 1')
            self.robot2_label: ui.label = ui.label('Robot 2')
            self.robot3_label: ui.label = ui.label('Robot 3')
            self.robot4_label: ui.label = ui.label('Robot 4')
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
        if self.game_manager.state == GameState.RUNNING:
            if self.debug:
                self.robot1_label.text = f"Robot 1: {self.game_manager.robot_states[Team.BLUE][0]}"
                self.robot2_label.text = f"Robot 2: {self.game_manager.robot_states[Team.BLUE][1]}"
                self.robot3_label.text = f"Robot 3: {self.game_manager.robot_states[Team.RED][0]}"
                self.robot4_label.text = f"Robot 4: {self.game_manager.robot_states[Team.RED][1]}"
        self.update_start_button(self.game_manager.state)
                
    def update_score(self, team: Team):
        if self.game_manager.state != GameState.RUNNING:
            self.score_display.text = f"{self.game_manager.score[Team.RED]} - {self.game_manager.score[Team.BLUE]}"
        else:
            self.game_manager.score[team] += 1
            self.score_display.text = f"{self.game_manager.score[Team.RED]} - {self.game_manager.score[Team.BLUE]}"
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