"""
MicroPython Script for XBee 3 Modules

Description:
    This script is designed to receive data from the Xbee Transmitter (Tx) and parse it for further processing. It is specifically tailored for use with XBee 3 Modules running the 802.15.4 firmware.

Author: Anway Pimpalkar
Date: 01/23/2024

"""

import xbee
from parse_string import parse_string
from sys import stdin, stdout

# Unique ID for each robot
ROBOT_ID = "BA"

# Parsing parameters
startLen = 1
timeLen = 4
robotIDLen = 2
coordLen = 3
angleLen = 3

# Store the parameters (Start Length, Time Length, Robot ID Length, Coordinate Length, Angle Length) in a list
parsingParameters = [startLen, timeLen, robotIDLen, coordLen, angleLen]

# Variable to store the last payload received
last_payload = None

while True:
    # Check if there is any data to be received in a non-blocking way
    payload = xbee.receive()

    # If there is data, store it in last_payload
    if payload:
        last_payload = payload

    # Read data from stdin
    data = stdin.buffer.read()

    # If data is received, start processing it
    if last_payload is not None:
        # Decode the payload
        receivedMsg = last_payload["payload"].decode("utf-8")

        # If the payload is not empty, parse it
        if receivedMsg:
            # Find the start and end of the payload
            start = receivedMsg.find(">")
            end = receivedMsg.find(";") + 1

            # If the start and end are found, parse the payload
            if start != -1 and end != -1:
                # Extract the string from the payload
                string = receivedMsg[start:end]

                # Parse the string
                parsedDict = parse_string(string, parsingParameters)

                # Check if the robot ID is a key in the dictionary
                if ROBOT_ID in parsedDict:
                    # If the robot ID is a key in the dictionary, set the match time, match bit, and robot coordinates to the values in the dictionary
                    matchTime = parsedDict["time"]
                    matchBit = parsedDict["matchbit"]
                    robotCoords = parsedDict[ROBOT_ID]

                else:
                    # If the robot ID is not a key in the dictionary, set the match time, match bit, and robot coordinates to 9s
                    matchTime = "9" * timeLen
                    matchBit = "9"
                    robotCoords = "9" * (coordLen * 2) + "9" * angleLen

                # Create output string for stdout (Arduino/UART interface)
                out = matchTime + "," + matchBit + "," + robotCoords

                # Write the output string to stdout
                stdout.buffer.write(out.encode())
