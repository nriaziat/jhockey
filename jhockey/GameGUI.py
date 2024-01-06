from fastapi import Response
from nicegui import Client, app, run, ui
from GameManager import GameState, GameManager, Team
from functools import partial
import time
import base64
import cv2 as cv
import numpy as np
import signal


black_1px = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAA1JREFUGFdjYGBg+A8AAQQBAHAgZQsAAAAASUVORK5CYII='
placeholder = Response(content=base64.b64decode(black_1px.encode('ascii')), media_type='image/png')

def convert(frame: np.ndarray) -> bytes:
    _, imencode_image = cv.imencode('.jpg', frame)
    return imencode_image.tobytes()


class GameGUI:
    '''
    Web GUI to control the game, add score, monitor time, and start/stop gameplay.
    Optionally, monitor video feed. 
    '''
    def __init__(self, start_time: int = 10, video_feed: bool = False):
        self.start_time = start_time
        self.video_feed = video_feed
        self.game_manager: GameManager = GameManager(start_time=start_time, video_feed=video_feed)
        # add a start/pause button and a reset button
        self.start_pause_button: ui.button = ui.button('Start', on_click=self.start_pause, color='green')
        self.reset_button: ui.button = ui.button('Reset', on_click=self.reset, color='red')
        # add a timer
        self.timer = ui.timer(1, self.update_timer)
        self.time_display = ui.label(f"{start_time // 60:02}:{start_time % 60:02}")
        # add a completion progress bar
        self.progress_bar = ui.linear_progress(show_value=False, size="25px")
        # add a score display
        self.score_display: ui.label = ui.label('0 - 0')
        # add score buttons
        self.red_score_button: ui.button = ui.button('Red Score', on_click=partial(self.update_score, team=Team.RED), color='red')
        self.blue_score_button: ui.button = ui.button('Blue Score', on_click=partial(self.update_score, team=Team.BLUE), color='blue')
        # add a live video feed
        if video_feed:
            self.video_feed = ui.interactive_image().classes('w-full h-full')
            self.video_timer = ui.timer(interval=0.1, callback=lambda: self.video_feed.set_source(f'/video/frame?{time.time()}'))

        ui.run()

    def start_pause(self):
        if self.game_manager.state == GameState.RUNNING:
            self.set_state(GameState.PAUSED)
        else:
            self.set_state(GameState.RUNNING)

    @app.get('/video/frame')
    async def update_video_feed(self):
        if not self.game_manager.camera.isOpened():
            return placeholder
        # The `video_capture.read` call is a blocking function.
        # So we run it in a separate thread (default executor) to avoid blocking the event loop.
        _, frame = await run.io_bound(self.game_manager.camera.read)
        if frame is None:
            return placeholder
        # `convert` is a CPU-intensive function, so we run it in a separate process to avoid blocking the event loop and GIL.
        jpeg = await run.cpu_bound(convert, frame)
        return Response(content=jpeg, media_type='image/jpeg')


    def reset(self):
        self.set_state(GameState.STOPPED)
        if self.video_feed:
            self.game_manager.camera.release()
        self.game_manager = GameManager(start_time=self.start_time, video_feed=self.video_feed)
        self.set_time(self.start_time)

    def update_timer(self):
        if self.game_manager.state == GameState.RUNNING:
            self.set_time(self.game_manager.time - 1)   
            if self.game_manager.time < 0:
                self.reset()

    def set_time(self, time: int):
        self.game_manager.time = time
        self.time_display.text = f"{self.game_manager.time // 60:02}:{self.game_manager.time % 60:02}"
        self.progress_bar.value = (self.start_time - self.game_manager.time) / self.start_time

    def update_score(self, team: Team):
        if self.game_manager.state != GameState.RUNNING:
            return
        self.game_manager.score[team.value] += 1
        self.score_display.text = f"{self.game_manager.score[Team.RED.value]} - {self.game_manager.score[Team.BLUE.value]}"
        self.set_state(GameState.PAUSED)

    def set_state(self, state: GameState):
        self.game_manager.state = state
        if state == GameState.STOPPED:
            self.start_pause_button.text = 'Start'
            self.set_time(self.start_time)
        elif state == GameState.RUNNING:
            self.start_pause_button.text = 'Pause'
        elif state == GameState.PAUSED:
            self.start_pause_button.text = 'Resume'

    async def disconnect(self) -> None:
        """Disconnect all clients from current running server."""
        for client_id in Client.instances:
            await app.sio.disconnect(client_id)

    async def cleanup(self) -> None:
        # This prevents ugly stack traces when auto-reloading on code change,
        # because otherwise disconnected clients try to reconnect to the newly started server.
        await self.disconnect()
        # Release the webcam hardware so it can be used by other applications again.
        if self.video_feed:
            self.game_manager.camera.release()

    def handle_sigint(self, signum, frame) -> None:
        # `disconnect` is async, so it must be called from the event loop; we use `ui.timer` to do so.
        ui.timer(0.1, self.disconnect, once=True)
        # Delay the default handler to allow the disconnect to complete.
        ui.timer(1, lambda: signal.default_int_handler(signum, frame), once=True)

if __name__ in {'__main__', "__mp_main__"}:
    g = GameGUI()    
    app.on_shutdown(g.cleanup)
    signal.signal(signal.SIGINT, g.handle_sigint)

