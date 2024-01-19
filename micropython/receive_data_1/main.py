import xbee
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

        receivedMsg = last_payload['payload'].decode('utf-8')


        if receivedMsg:
            
            # stdout.buffer.write(str(receivedMsg + '\n').encode())

            startString = receivedMsg.find("{")
            endString = receivedMsg.find("}", startString)

            string = receivedMsg[startString:endString]
            
            if endString == -1:
                receivedMsg2 = xbee.receive()['payload'].decode('utf-8')
                endString2 = receivedMsg.find("}")

                if endString2 < receivedMsg2.find("{"):
                    string = string + receivedMsg2[:(endString2 + 1)]

            string = receivedMsg[startString + 1:endString]

            string = string.replace("'", "")
            string = string.split(", ")
            string = [x.split(": ") for x in string]
            data = {x[0]: x[1] for x in string}

            out = str(data["match"]) + "," + str(data["time"]) + "," + str(data[ROBOT_ID]) + "\n"

            stdout.buffer.write(out.encode())