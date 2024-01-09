from .utils import GameState, Team
from functools import partial
import time
from typing import Protocol
import numpy as np
import signal
from fastapi import Response
from nicegui import Client, app, run, ui
import base64
import cv2 as cv

black_1px = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAA1JREFUGFdjYGBg+A8AAQQBAHAgZQsAAAAASUVORK5CYII='
placeholder = Response(content=base64.b64decode(black_1px.encode('ascii')), media_type='image/png')


class Camera(Protocol):
	def read(self) -> np.ndarray:
		'''
		Returns the frame from the camera.
		'''
		...

def format_score(team: Team, score: int) -> str:
	return f"{team.name}: {score} "

class GameGUI:
	'''
	Web GUI to control the game, add score, monitor time, and start/stop gameplay.
	Optionally, monitor video feed. 

	'''
	def __init__(self, * , cam: Camera = None, video_feed: bool = False):
		self.cam: Camera = cam
		self.video_feed: bool = video_feed
		self.state = GameState.STOPPED
		self.toggle_state = False
		self.reset_state = False
		self.seconds_remaining: int = None
		self.score = None
		self.add_score = None
		if self.video_feed:
			self.video_feed: ui.interactive_image = ui.interactive_image().classes('w-3/4')
			with self.video_feed:
				self.score_display = ui.label('').classes('absolute-bottom text-subtitle2 text-center')
			self.video_timer = ui.timer(interval=0.1, callback=lambda: self.video_feed.set_source(f'/video/frame?{time.time()}'))
		else:
			self.score_display = ui.label('').classes('text-subtitle2 text-center')
		

		self.debug: bool = False
		with ui.column().bind_visibility_from(self, 'debug'):
			columns = [
				{'name': 'robot', 'label': 'Name', 'field': 'robot', 'required': True, 'align': 'left'},
				{'name': 'x', 'label': 'x [mm]', 'field': 'x', 'sortable': True},
				{'name': 'y', 'label': 'y [mm]', 'field': 'y', 'sortable': True},
				{'name': 'theta', 'label': 'theta [deg]', 'field': 'theta', 'sortable': True},
			]
			self.debug_table = ui.table(columns=columns, rows=[], row_key='robot')
		app.on_shutdown(self.cleanup)
		signal.signal(signal.SIGINT, handle_sigint)
		ui.run(title='JHockey')

	def create_ui(self, match_length_sec: int):
		self.match_length_sec = match_length_sec
		self.seconds_remaining = match_length_sec
		with ui.row():
			self.start_pause_button: ui.button = ui.button('Start', on_click=self.start_pause, color='green')
			self.reset_button: ui.button = ui.button('Reset', on_click=self.reset, color='red')
			self.red_score_button: ui.button = ui.button('Red Score', 
														 on_click=partial(self.update_score, team=Team.RED), color='red')
			self.blue_score_button: ui.button = ui.button('Blue Score',
														  on_click=partial(self.update_score, team=Team.BLUE), color='blue')    
			self.progress_bar = ui.circular_progress(show_value=True, size="xl", 
													min=0, max=self.match_length_sec).bind_value_from(self, 'seconds_remaining')
			self.debug_button: ui.button = ui.button('Debug Mode', on_click=self.toggle_debug, color='orange')

	def toggle_debug(self):
		self.debug = not self.debug

	def start_pause(self):
		self.toggle_state = True

	def reset(self):
		self.reset_state = True

	def update(self, data: dict):
		self.state = data['state']
		self.toggle_state = False
		self.reset_state = False
		self.add_score = None
		self.score = data['score']
		self.score_display.text = data['score_as_string']
		self.seconds_remaining = data['seconds_remaining']
		robot_states = data['robot_states']
		if self.debug:
			rows = [
				{'robot': 'Red 1', 'x': robot_states[Team.RED][0].x, 'y': robot_states[Team.RED][0].y, 'theta': robot_states[Team.RED][0].theta},
				{'robot': 'Red 2', 'x': robot_states[Team.RED][1].x, 'y': robot_states[Team.RED][1].y, 'theta': robot_states[Team.RED][1].theta},
				{'robot': 'Blue 1', 'x': robot_states[Team.BLUE][0].x, 'y': robot_states[Team.BLUE][0].y, 'theta': robot_states[Team.BLUE][0].theta},
				{'robot': 'Blue 2', 'x': robot_states[Team.BLUE][1].x, 'y': robot_states[Team.BLUE][1].y, 'theta': robot_states[Team.BLUE][1].theta},
			]
			self.debug_table.rows = rows
		self.update_start_button(self.state)
				
	def update_score(self, team: Team):
		if self.state == GameState.RUNNING:
			self.add_score = team
			self.toggle_state = True

	def update_start_button(self, state: GameState):
		if state == GameState.STOPPED:
			self.start_pause_button.text = 'Start'
		elif state == GameState.RUNNING:
			self.start_pause_button.text = 'Pause'
		elif state == GameState.PAUSED:
			self.start_pause_button.text = 'Resume'

	async def cleanup(self) -> None:
		# This prevents ugly stack traces when auto-reloading on code change,
		# because otherwise disconnected clients try to reconnect to the newly started server.
		await disconnect()
		# Release the webcam hardware so it can be used by other applications again.

	@app.get('/video/frame')
	async def update_video_feed(self) -> Response:
		print("Update video feed")
		# So we run it in a separate thread (default executor) to avoid blocking the event loop.
		frame = self.cam.read()
		if frame is None:
			return placeholder
		# `convert` is a CPU-intensive function, so we run it in a separate process to avoid blocking the event loop and GIL.
		jpeg = await run.cpu_bound(convert, frame)
		return Response(content=jpeg, media_type='image/jpeg')


def convert(frame: np.ndarray) -> bytes:
	_, imencode_image = cv.imencode('.jpg', frame)
	return imencode_image.tobytes()

async def disconnect() -> None:
	"""Disconnect all clients from current running server."""
	for client_id in Client.instances:
		await app.sio.disconnect(client_id)

def handle_sigint(signum, frame) -> None:
	# `disconnect` is async, so it must be called from the event loop; we use `ui.timer` to do so.
	ui.timer(0.1, disconnect, once=True)
	# Delay the default handler to allow the disconnect to complete.
	ui.timer(1, lambda: signal.default_int_handler(signum, frame), once=True)