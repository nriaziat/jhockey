def parse_string(data):
    # Define the lengths of each field
    start_len = 1
    time_len = 6
    match_len = 1

    robot_id_len = 2
    robot_coord_len = 4
    robot_angle_len = 2

    # Initialize the dictionary to store the parsed data
    parsed_data = {
        "start": data[0:start_len],
        "time": data[start_len : start_len + time_len],
        "match": data[start_len + time_len : start_len + time_len + match_len],
    }

    # Set the initial index after the start, time, and match fields
    current_index = start_len + time_len + match_len

    # Iterate to parse each robot's data
    for i in range(4):
        # Extract each field for the robot
        robot_id = data[current_index : current_index + robot_id_len]
        current_index += robot_id_len

        robot_x_coord = data[current_index : current_index + robot_coord_len]
        current_index += robot_coord_len

        robot_y_coord = data[current_index : current_index + robot_coord_len]
        current_index += robot_coord_len

        robot_angle = data[current_index : current_index + robot_angle_len]
        current_index += robot_angle_len

        # Store the robot's data in the dictionary
        parsed_data[robot_id] = {
            str(robot_x_coord) + "," + str(robot_y_coord) + "," + str(robot_angle)
        }

    return parsed_data
