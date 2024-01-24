from .types import GameState, Team, GUIData
from functools import partial
import time
import signal
from nicegui import Client, app, ui
import logging


def format_score(team: Team, score: int) -> str:
    return f"{team.name}: {score} "


class GameGUI:
    """
    Web GUI to control the game, add score, monitor time, and start/stop gameplay.
    """

    def __init__(self):
        self.state = GameState.STOPPED
        self.toggle_state = False
        self.reset_state = False
        self.seconds_remaining: int = None
        self.score = None
        self.add_score = None
        self.last_update_time = time.time()
        self.camera_connected = False

    def create_ui(self, match_length_sec: int):
        self.match_length_sec = match_length_sec
        self.seconds_remaining = match_length_sec

        self.score_display = ui.label("").classes("text-subtitle2 text-center")

        self.debug: bool = False
        with ui.column().bind_visibility_from(self, "debug"):
            robot_columns = [
                {
                    "name": "robot",
                    "label": "Name",
                    "field": "robot",
                    "required": True,
                    "align": "left",
                    "sortable": True,
                },
                {"name": "x", "label": "x [mm]", "field": "x"},
                {"name": "y", "label": "y [mm]", "field": "y"},
                {"name": "theta", "label": "Heading [millirad]", "field": "theta"},
                {"name": "found", "label": "Found", "field": "found"},
            ]
            self.robot_debug_tab = ui.table(
                columns=robot_columns, rows=[], row_key="robot"
            )
            self.update_rate = ui.label("")

            tag_columns = [
                {
                    "name": "id",
                    "label": "ID",
                    "field": "id",
                    "required": True,
                    "align": "left",
                    "sortable": True,
                },
                {"name": "x", "label": "x [px]", "field": "x"},
                {"name": "y", "label": "y [px]", "field": "y"}
            ]
            self.tag_debug_tab = ui.table(columns=tag_columns, rows=[], row_key="id")

            self.loop_rate_indicator = ui.label("")

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
            self.camera_connected = (
                ui.icon("videocam", color="green")
                .bind_visibility_from(self, "camera_connected")
                .classes("text-5xl")
            )
            self.camera_disconnected = (
                ui.icon("videocam_off", color="red")
                .bind_visibility_from(self, "camera_connected", value=False)
                .classes("text-5xl")
            )
        app.on_shutdown(self.cleanup)
        signal.signal(signal.SIGINT, handle_sigint)

    def toggle_debug(self):
        self.debug = not self.debug

    def start_pause(self):
        self.toggle_state = True

    def reset(self):
        self.reset_state = True

    def update(self, data: GUIData):
        logging.info("GameGUI updated, state: %s", data.state.name)
        self.toggle_state = False
        self.reset_state = False
        self.state = data.state
        self.add_score = None
        self.score = data.score
        self.score_display.text = data.score_as_string
        self.seconds_remaining = data.seconds_remaining
        self.camera_connected = data.cam_connected
        robot_states = data.robot_states
        aruco_tags = data.aruco_tags
        if robot_states is not None and self.debug:
            robot_rows = [
                {
                    "robot": id,
                    "x": robot_states[id].x,
                    "y": robot_states[id].y,
                    "theta": robot_states[id].heading,
                    "found": "✅" if robot_states[id].found else "❌",
                }
                for id in robot_states
            ]
            self.robot_debug_tab.rows = robot_rows

        if self.debug:
            tag_rows = []
            for tag in sorted(aruco_tags, key=lambda tag: tag.id):
                tag_rows.append(
                    {
                        "id": tag.id,
                        "x": f"{tag.center.x:.2f}",
                        "y": f"{tag.center.y:.2f}",
                    }
                )
            
            self.tag_debug_tab.rows = tag_rows
            self.loop_rate_indicator.text = f"Loop Rate: {data.loop_rate:.1e} Hz"

        self.update_start_button(self.state)
        try:
            update_rate = 1 / (time.time() - self.last_update_time)
        except ZeroDivisionError:
            update_rate = 0
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
