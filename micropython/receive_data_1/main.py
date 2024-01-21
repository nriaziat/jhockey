import xbee
from parse_string import parse_string
from sys import stdin, stdout

ROBOT_ID = "BA"

last_payload = None

while True:
    payload = xbee.receive()

    if payload:
        last_payload = payload

    data = stdin.buffer.read()

    # if data:

    # if data.decode() == "?" and last_payload is not None:

    if last_payload is not None:
        receivedMsg = last_payload["payload"].decode("utf-8")

        if receivedMsg:
            start = receivedMsg.find(">")
            end = receivedMsg.find(">", start + 1)

            if end != -1:
                string = receivedMsg[start + 1 : end]

            else:
                payload2 = xbee.receive()
                receivedMsg2 = payload2["payload"].decode("utf-8")

                start2 = receivedMsg2.find(">")
                string = receivedMsg[start + 1 :] + receivedMsg2[0:start2]

            parsed_string = parse_string(string)

            out = (
                parsed_string["time"]
                + ","
                + parsed_string["matchbit"]
                + ","
                + parsed_string[ROBOT_ID]
            )

            stdout.buffer.write(out.encode())
