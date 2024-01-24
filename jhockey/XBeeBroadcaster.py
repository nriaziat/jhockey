from __future__ import annotations
from threading import Thread
from .types import BroadcasterMessage
from digi.xbee.devices import XBeeDevice

class XBeeBroadcaster:
    """
    Class to broadcast location information to each team via XBee protocol.
    """

    def __init__(self, port="/dev/ttyUSB0"):
        self.xbee = XBeeDevice(port, 115200)
        self.xbee.open()

    def broadcast(self, msg: BroadcasterMessage):
        """
        Broadcasts data to robots.
        @param data: BroadcasterMessage to broadcast
        """
        self.xbee.send_data_broadcast(str(msg))
