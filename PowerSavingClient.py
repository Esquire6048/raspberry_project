import socket
import os
import sys
import subprocess
import requests
import json
import time


def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


try:
    import Quartz
except ImportError:
    print("Installing required libraries...")
    install_package('pyobjc-framework-Quartz')
    import Quartz

SLACK_URL_POST = 'https://slack.com/api/chat.postMessage'
SLACK_WORKSPACE_TOKEN = ''
SLACK_CHANNEL_ID = 'D07BZT4AFPZ'


def shutdown_screen():
    os.system('pmset displaysleepnow')


def is_screen_locked():
    if Quartz.CGDisplayIsAsleep(Quartz.CGMainDisplayID()):
        return True
    else:
        return False


def send_msg2slack():
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    data = {
        "token": SLACK_WORKSPACE_TOKEN,
        "channel": SLACK_CHANNEL_ID,
        "blocks": json.dumps([
            {
                "type": "section",
                "text": {
                        "type": "mrkdwn",
                    "text": f"*:red_circle: CAUTION*\nThe system turned off the screen at <mailto:y-ouyang@mc.net.ist.osaka-u.ac.jp|{t}>."
                }
            }
        ])
    }
    response = requests.post(SLACK_URL_POST, data=data)
    if response.status_code == 200 and response.json().get("ok"):
        print("Slack message sent successfully")
    else:
        print(f"Failed to send Slack message: {response.text}")


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 3000))
    server_socket.listen(5)

    print("Client listening on port 3000...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr} has been established.")
        data = client_socket.recv(1024)
        if data:
            if is_screen_locked():
                print("Screen is already locked")
            else:
                print("Received request, shutting down screen...")
                shutdown_screen()
                send_msg2slack()
        client_socket.close()


if __name__ == "__main__":
    start_server()
