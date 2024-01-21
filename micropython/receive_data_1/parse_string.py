def parse_string(data_str):
    parts = data_str.split(",")

    data = {
        "time": parts[0][1:],
        "matchbit": parts[1],
        parts[2]: str(parts[3]) + "," + str(parts[4]) + "," + str(parts[5]),
        parts[6]: str(parts[7]) + "," + str(parts[8]) + "," + str(parts[9]),
        parts[10]: str(parts[11]) + "," + str(parts[12]) + "," + str(parts[13]),
        parts[14]: str(parts[15]) + "," + str(parts[16]) + "," + str(parts[17]),
    }

    return data
