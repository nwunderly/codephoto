import os
import subprocess
import time

import dotenv

dotenv.load_dotenv()

# must be done after loading dotenv
import cv2

VIDEO_SOURCE = int(os.getenv("VIDEO_SOURCE"))


def get_screen_resolution():
    # Get screen resolution on Linux
    output = subprocess.check_output(["xrandr"]).decode()

    screen_width = None
    screen_height = None

    # Parse for current resolution (bit hacky but works)
    for line in output.split("\n"):
        if "*" in line:
            resolution = line.split()[0]
            screen_width, screen_height = map(int, resolution.split("x"))
            break

    if not (screen_width and screen_height):
        raise Exception("Failed to get screen size")

    return screen_width, screen_height


def test_webcam():
    print("Starting up...")

    # open gedit
    proc = subprocess.Popen(["gedit"])
    time.sleep(2)

    # Open the default camera (index 0)
    # Change the index if you have multiple cameras (e.g., 1, 2)
    cap = cv2.VideoCapture(VIDEO_SOURCE)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open video stream or file.")
        return

    print("Webcam stream started. Press ctrl-c or q to quit.")

    try:
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()

            if not ret:
                print("Error: Failed to capture image.")
                break

            window_name = "Webcam"
            cv2.namedWindow(window_name)

            # Display the resulting frame
            cv2.imshow("Webcam", frame)

            # Get monitor/window dimensions
            screen_width, screen_height = get_screen_resolution()
            _, _, window_width, window_height = cv2.getWindowImageRect(window_name)

            # Position at bottom right
            x = screen_width - window_width - 10
            y = screen_height - window_height - 50
            cv2.moveWindow(window_name, x, y)

            # Press 'q' on the keyboard to exit the loop
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        # When everything done, release the capture and destroy all windows
        cap.release()
        cv2.destroyAllWindows()

        # kill gedit
        if proc.poll() is None:
            proc.kill()


if __name__ == "__main__":
    test_webcam()
