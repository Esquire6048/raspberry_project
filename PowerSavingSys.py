### Imports ###################################################################

from picamera.array import PiRGBArray
from picamera import PiCamera

import multiprocessing as mp
import time
import cv2
import socket
import requests
import json

DEVICE_IP = '100.64.1.112'
DEVICE_PORT = 3000
TIMEOUT_CONST = 15

### Setup #####################################################################

resX = 320
resY = 240

# Setup the camera
camera = PiCamera()
camera.resolution = (resX, resY)
camera.framerate = 30

fps = 0
t_start = time.time()

# Use this as our output
rawCapture = PiRGBArray(camera, size=(resX, resY))

# load eye cascade file
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_eye_tree_eyeglasses.xml"
)

# for conditional judgment
previous_value = 0
timer = time.time()
timer_running = True

info = ""

### Helper Functions ##########################################################


def send_msg2client():
    message = "Timeout"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((DEVICE_IP, DEVICE_PORT))
            s.sendall(message.encode())
            print(f"Sent message: {message}")
        except Exception as e:
            print(f"Failed to send message: {e}")


def get_eyes(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return face_cascade.detectMultiScale(gray), img


def draw_frame(img, faces):
    global fps
    global previous_value
    global timer
    global timer_running
    global info

    eye_count = len(faces)
    new_value = 1 if eye_count > 0 else 0
    if new_value != previous_value:
        previous_value = new_value
        if new_value == 0:
            timer = time.time()
            timer_running = True
        elif previous_value == 1:
            timer_running = False
            info = "Active"

    if timer_running:
        elapsed_time = time.time() - timer
        minutes, seconds = divmod(
            max(0, TIMEOUT_CONST + 1 - elapsed_time), 60)
        info = f"will turn off the screen after {int(minutes):02}m{int(seconds):02}s"
        if elapsed_time >= TIMEOUT_CONST:  # Timeout
            send_msg2client()
            info = "Inactive"
            timer_running = False

    # draw rectangle around every eyes
    for x, y, w, h in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (200, 255, 0), 2)

    # calculate and show the FPS
    fps = fps + 1
    sfps = fps / (time.time() - t_start)
    cv2.putText(img, "FPS : " + str(int(sfps)), (10, 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    # show appropriate info text
    cv2.putText(img, info, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    cv2.imshow("Frame", img)

### Main ######################################################################


if __name__ == "__main__":
    pool = mp.Pool(processes=4)

    i = 0
    rList = [None] * 17
    fList = [None] * 17
    iList = [None] * 17

    camera.capture(rawCapture, format="bgr")

    for x in range(17):
        rList[x] = pool.apply_async(get_eyes, [rawCapture.array])
        fList[x], iList[x] = rList[x].get()
        fList[x] = []

    rawCapture.truncate(0)

    for frame in camera.capture_continuous(
        rawCapture, format="bgr", use_video_port=True
    ):
        image = frame.array
        image = cv2.flip(image, 0)

        if i == 1:
            rList[1] = pool.apply_async(get_eyes, [image])
            draw_frame(iList[2], fList[1])

        elif i == 2:
            iList[2] = image
            draw_frame(iList[3], fList[1])

        elif i == 3:
            iList[3] = image
            draw_frame(iList[4], fList[1])

        elif i == 4:
            iList[4] = image
            fList[5], iList[5] = rList[5].get()
            draw_frame(iList[5], fList[5])

        elif i == 5:
            rList[5] = pool.apply_async(get_eyes, [image])
            draw_frame(iList[6], fList[5])

        elif i == 6:
            iList[6] = image
            draw_frame(iList[7], fList[5])

        elif i == 7:
            iList[7] = image
            draw_frame(iList[8], fList[5])

        elif i == 8:
            iList[8] = image
            fList[9], iList[9] = rList[9].get()
            draw_frame(iList[9], fList[9])

        elif i == 9:
            rList[9] = pool.apply_async(get_eyes, [image])
            draw_frame(iList[10], fList[9])

        elif i == 10:
            iList[10] = image
            draw_frame(iList[11], fList[9])

        elif i == 11:
            iList[11] = image
            draw_frame(iList[12], fList[9])

        elif i == 12:
            iList[12] = image
            fList[13], iList[13] = rList[13].get()
            draw_frame(iList[13], fList[13])

        elif i == 13:
            rList[13] = pool.apply_async(get_eyes, [image])
            draw_frame(iList[14], fList[13])

        elif i == 14:
            iList[14] = image
            draw_frame(iList[15], fList[13])

        elif i == 15:
            iList[15] = image
            draw_frame(iList[16], fList[13])

        elif i == 16:
            iList[16] = image
            fList[1], iList[1] = rList[1].get()
            draw_frame(iList[1], fList[1])

            i = 0

        i += 1

        rawCapture.truncate(0)

        # exit if Esc key is pressed
        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()
