import socket
from threading import Thread
from time import sleep

PORT = 12345
HOST = "0.0.0.0"

DESTINATION = "172.20.10.13"  # TODO: this need to change for each user
# DESTINATION = "172.20.10.6"  # TODO: this need to change for each user


def p_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print("the server is online...")

    client, address = server_socket.accept()
    print(f"connected to {address} on port {PORT}")
    while True:
        data = client.recv(1024)
        # TODO: Write other robots values to memory
        print(data)


def p_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected = False

    while not connected:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((DESTINATION, PORT))
            connected = True
        except Exception as e:
            client_socket.close()
            print(e)  # print the error
            sleep(1)  # retry connection in 1 second

    while True:
        # TODO: write own robots values to socket
        client_socket.send(bytes("x,y,z", "UTF-8"))
        sleep(1)


# def format_data(x, y, z, ...):
#     return data

if __name__ == "__main__":
    Thread(target=p_server).start()
    Thread(target=p_client).start()
