from .utils import GameState, Team, GUIData
from functools import partial
import time
import signal
from nicegui import Client, app, ui


def format_score(team: Team, score: int) -> str:
    return f"{team.name}: {score} "


class GameGUI:
    """
    Web GUI to control the game, add score, monitor time, and start/stop gameplay.
    """

    def __init__(self, *, video_feed: bool = False):
        """
        Parameters
        ----------
        video_feed : bool, optional
            Whether to display a video feed of the game, by default False
        """
        self.video_feed: bool = video_feed
        self.state = GameState.STOPPED
        self.toggle_state = False
        self.reset_state = False
        self.seconds_remaining: int = None
        self.score = None
        self.add_score = None
        self.last_update_time = time.time()

    def create_ui(self, match_length_sec: int):
        self.match_length_sec = match_length_sec
        self.seconds_remaining = match_length_sec
        if self.video_feed:
            self.video_feed: ui.interactive_image = ui.interactive_image().classes(
                "w-3/4"
            )
            with self.video_feed:
                self.score_display = ui.label("").classes(
                    "absolute-bottom text-subtitle2 text-center"
                )
            self.video_timer = ui.timer(
                interval=0.05,
                callback=lambda: self.video_feed.set_source(
                    f"/video/frame?{time.time()}"
                ),
            )
        else:
            self.score_display = ui.label("").classes("text-subtitle2 text-center")

        self.debug: bool = False
        with ui.column().bind_visibility_from(self, "debug"):
            columns = [
                {"name": "robot", "label": "Name", "field": "robot", "required": True, "align": "left", "sortable": True},
                {"name": "x", "label": "x [mm]", "field": "x"},
                {"name": "y", "label": "y [mm]", "field": "y"},
                {"name": "theta","label": "theta [deg]", "field": "theta"},
                {"name": "found", "label": "Found", "field": "found"}
            ]
            self.debug_table = ui.table(columns=columns, rows=[], row_key="robot")
            self.update_rate = ui.label("")

        with ui.row():
            self.start_pause_button: ui.button = ui.button(
                "Start", on_click=self.start_pause, color="green"
            )
            self.reset_button: ui.button = ui.button(
                "Reset", on_click=self.reset, color="red"
            )
            self.red_score_button: ui.button = ui.button(
                "Red Score",
                on_click=partial(self.update_score, team=Team.RED),
                color="red",
            )
            self.blue_score_button: ui.button = ui.button(
                "Blue Score",
                on_click=partial(self.update_score, team=Team.BLUE),
                color="blue",
            )
            self.progress_bar = ui.circular_progress(
                show_value=True, size="xl", min=0, max=self.match_length_sec
            ).bind_value_from(self, "seconds_remaining")
            self.debug_button: ui.button = ui.button(
                "Debug Mode", on_click=self.toggle_debug, color="orange"
            )
        app.on_shutdown(self.cleanup)
        signal.signal(signal.SIGINT, handle_sigint)
        ui.run(title="JHockey")

    def toggle_debug(self):
        self.debug = not self.debug

    def start_pause(self):
        self.toggle_state = True

    def reset(self):
        self.reset_state = True

    def update(self, data: GUIData):
        self.state = data.state
        self.toggle_state = False
        self.reset_state = False
        self.add_score = None
        self.score = data.score
        self.score_display.text = data.score_as_string
        self.seconds_remaining = data.seconds_remaining
        robot_states = data.robot_states
        if robot_states is not None and self.debug:
            rows = [
                {
                    "robot": "Red 1",
                    "x": robot_states[Team.RED][0].x,
                    "y": robot_states[Team.RED][0].y,
                    "theta": robot_states[Team.RED][0].theta,
                    "found": "✅" if robot_states[Team.RED][0].found else "❌"
                },
                {
                    "robot": "Red 2",
                    "x": robot_states[Team.RED][1].x,
                    "y": robot_states[Team.RED][1].y,
                    "theta": robot_states[Team.RED][1].theta,
                    "found": "✅" if robot_states[Team.RED][1].found else "❌"
                },
                {
                    "robot": "Blue 1",
                    "x": robot_states[Team.BLUE][0].x,
                    "y": robot_states[Team.BLUE][0].y,
                    "theta": robot_states[Team.BLUE][0].theta,
                    "found": "✅" if robot_states[Team.BLUE][0].found else "❌"
                },
                {
                    "robot": "Blue 2",
                    "x": robot_states[Team.BLUE][1].x,
                    "y": robot_states[Team.BLUE][1].y,
                    "theta": robot_states[Team.BLUE][1].theta,
                    "found": "✅" if robot_states[Team.BLUE][1].found else "❌"
                },
            ]
            self.debug_table.rows = rows
        self.update_start_button(self.state)
        update_rate = 1 / (time.time() - self.last_update_time)
        self.last_update_time = time.time()
        self.update_rate.text = f"GUI Update Rate: {update_rate:.1e} Hz"

    def update_score(self, team: Team):
        if self.state == GameState.RUNNING:
            self.add_score = team
            self.toggle_state = True

    def update_start_button(self, state: GameState):
        match state:
            case GameState.STOPPED:
                self.start_pause_button.text = "Start"
            case GameState.RUNNING:
                self.start_pause_button.text = "Pause"
            case GameState.PAUSED:
                self.start_pause_button.text = "Resume"

    async def cleanup(self) -> None:
        # This prevents ugly stack traces when auto-reloading on code change,
        # because otherwise disconnected clients try to reconnect to the newly started server.
        await disconnect()
        # Release the webcam hardware so it can be used by other applications again.


async def disconnect() -> None:
    """Disconnect all clients from current running server."""
    for client_id in Client.instances:
        await app.sio.disconnect(client_id)


def handle_sigint(signum, frame) -> None:
    # `disconnect` is async, so it must be called from the event loop; we use `ui.timer` to do so.
    ui.timer(0.1, disconnect, once=True)
    # Delay the default handler to allow the disconnect to complete.
    ui.timer(1, lambda: signal.default_int_handler(signum, frame), once=True)
