import socket
import os

def shutdown_screen():
    os.system('pmset displaysleepnow')

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 3000))
    server_socket.listen(5)

    print("Server listening on port 3000...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr} has been established.")
        data = client_socket.recv(1024)
        if data:
            print("Received data, shutting down screen...")
            shutdown_screen()
        client_socket.close()

if __name__ == "__main__":
    start_server()
