import cv2
import cv2.aruco as aruco
import pathlib


def calibrate_charuco(dirpath, image_format, marker_length, square_length):
    """Apply camera calibration using aruco.
    The dimensions are in cm.
    """
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_1000)
    board = aruco.CharucoBoard(size=(5, 7), 
                               square_length=square_length, 
                               marker_length=marker_length, 
                               aruco_dict=aruco_dict)
    arucoParams = aruco.DetectorParameters()
    detector = cv2.aruco.CharucoDetector(aruco_dict, arucoParams)
    counter, corners_list, id_list = [], [], []
    img_dir = pathlib.Path(dirpath)
    first = 0
    # Find the ArUco markers inside each image
    for img in img_dir.glob(f'*{image_format}'):
        print(f'using image {img}')
        image = cv2.imread(str(img))
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = aruco.detectMarkers(
            img_gray,
            aruco_dict,
            parameters=arucoParams
        )

        resp, charuco_corners, charuco_ids = aruco.interpolateCornersCharuco(
            markerCorners=corners,
            markerIds=ids,
            image=img_gray,
            board=board
        )
        # If a Charuco board was found, let's collect image/corner points
        # Requiring at least 20 squares
        if resp > 20:
            # Add these corners and ids to our calibration arrays
            corners_list.append(charuco_corners)
            id_list.append(charuco_ids)

    # Actual calibration
    ret, mtx, dist, rvecs, tvecs = aruco.calibrateCameraCharuco(
        charucoCorners=corners_list,
        charucoIds=id_list,
        board=board,
        imageSize=img_gray.shape,
        cameraMatrix=None,
        distCoeffs=None)

    return [ret, mtx, dist, rvecs, tvecs]