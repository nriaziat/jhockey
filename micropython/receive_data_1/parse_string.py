def parse_string(data):
    startLen = 1
    timeLen = 4
    robotIDLen = 2
    coordLen = 3
    angleLen = 3

    parsedData = {}

    parsedData["start"] = data[0:startLen]
    parsedData["time"] = data[startLen : startLen + timeLen]
    parsedData["matchbit"] = data[startLen + timeLen]

    i = startLen + timeLen + 1

    while i < len(data):
        toCheck = data[i:]

        robotName = toCheck[0:robotIDLen]
        parsedData[robotName] = (
            toCheck[robotIDLen : robotIDLen + coordLen]
            + ","
            + toCheck[robotIDLen + coordLen : robotIDLen + (coordLen * 2)]
            + ","
            + toCheck[
                robotIDLen + (coordLen * 2) : robotIDLen + (coordLen * 2) + angleLen
            ]
        )

        i = i + 11

        if data[i] == ";":
            break

    return parsedData
