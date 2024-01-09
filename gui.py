from jhockey.GameGUI import GameGUI

import signal
from fastapi import Response
from nicegui import Client, app, run, ui
import base64
import cv2 as cv
import numpy as np

black_1px = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAA1JREFUGFdjYGBg+A8AAQQBAHAgZQsAAAAASUVORK5CYII='
placeholder = Response(content=base64.b64decode(black_1px.encode('ascii')), media_type='image/png')

def convert(frame: np.ndarray) -> bytes:
    _, imencode_image = cv.imencode('.jpg', frame)
    return imencode_image.tobytes()
async def disconnect() -> None:
    """Disconnect all clients from current running server."""
    for client_id in Client.instances:
        await app.sio.disconnect(client_id)

async def cleanup() -> None:
    # This prevents ugly stack traces when auto-reloading on code change,
    # because otherwise disconnected clients try to reconnect to the newly started server.
    await disconnect()
    # Release the webcam hardware so it can be used by other applications again.
    camera.release()

def handle_sigint(signum, frame) -> None:
    # `disconnect` is async, so it must be called from the event loop; we use `ui.timer` to do so.
    ui.timer(0.1, disconnect, once=True)
    # Delay the default handler to allow the disconnect to complete.
    ui.timer(1, lambda: signal.default_int_handler(signum, frame), once=True)

@app.get('/video/frame')
async def update_video_feed() -> Response:
    if not camera.isOpened():
        return placeholder
    # The `video_capture.read` call is a blocking function.
    # So we run it in a separate thread (default executor) to avoid blocking the event loop.
    _, frame = await run.io_bound(camera.read)
    if frame is None:
        return placeholder
    # `convert` is a CPU-intensive function, so we run it in a separate process to avoid blocking the event loop and GIL.
    jpeg = await run.cpu_bound(convert, frame)
    return Response(content=jpeg, media_type='image/jpeg')

app.on_shutdown(cleanup)
signal.signal(signal.SIGINT, handle_sigint)