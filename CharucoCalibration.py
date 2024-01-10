from jhockey.Charuco import calibrate_charuco
from utils import save_coefficients

# Parameters
IMAGES_DIR = "path_to_images"
IMAGES_FORMAT = "jpg"
# Dimensions in cm
MARKER_LENGTH = 2.7
SQUARE_LENGTH = 3.2


if __name__ == "__main__":
    # Calibrate
    ret, mtx, dist, rvecs, tvecs = calibrate_charuco(
        IMAGES_DIR, IMAGES_FORMAT, MARKER_LENGTH, SQUARE_LENGTH
    )
    # Save coefficients into a file
    save_coefficients(mtx, dist, "calibration_charuco.yml")
