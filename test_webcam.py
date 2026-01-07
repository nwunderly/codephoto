import os
import subprocess
import time

import dotenv
dotenv.load_dotenv()

import cv2

VIDEO_SOURCE = int(os.getenv("VIDEO_SOURCE"))

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

            # Display the resulting frame
            cv2.imshow('Webcam Test', frame)

            # Press 'q' on the keyboard to exit the loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
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
