import socket
from threading import Thread
from time import sleep
import multiprocessing as mp
import time

PORT = 12345
HOST = "0.0.0.0"
DELAY = 0.5 # Delay in seconds

DESTINATION = "172.20.10.13"  # TODO: this need to change for each user
# DESTINATION = "172.20.10.6"  # TODO: this need to change for each user

# Global variable to indicate if threads should stop
should_stop = mp.Event()

# Initialising global dummy variables for now (change later)
global_x = mp.Value("f", 0.0) # probably should be initialised to a purposeful value in loading zone
global_y = mp.Value("f", 0.0) # probably should be initialised to a purposeful value in loading zone
global_theta = mp.Value("f", 90.0) # could be 0 to start off with
global_mode = mp.Value("c", b'L') # either L or G. start in loading zone
global_lane = mp.Value("c", b' ') # either A B or C

def p_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print("the server is online...")

    client, address = server_socket.accept()
    print(f"connected to {address} on port {PORT}")
    while True:
        data = client.recv(1024)
        decoded_data = data.decode("utf-8")
        variables = decoded_data.split(',')
        x = variables[0]
        y = variables[1]
        theta = variables[2]
        mode = variables[3]
        lane = variables[4]
        print(f"{x},{y},{theta},{mode},{lane}")

def p_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected = False

    while not connected:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((DESTINATION, PORT))
            connected = True
            print("client connected successfully")
        except Exception as e:
            print("exception 1 handled")
            client_socket.close()
            print(e)  # print the error
            sleep(1)  # retry connection in 1 second

    while True:
        try:
            if should_stop.is_set():
                break # Exit the loop if keyboard interrupt occurs
            text = f'{global_x.value},{global_y.value},{global_theta.value},{global_mode.value},{global_lane.value}'
            client_socket.send(bytes(text, "UTF-8"))
            sleep(DELAY)
        except Exception as e:
            print("exception 2 handled")
            client_socket.close()
            print(e)  # print the error

if __name__ == "__main__":
    Thread(target=p_server).start()
    Thread(target=p_client).start()
    try:
        while not should_stop.is_set():
            # Dummy global variables to test this function
            for i in range(50):
                # print(f"{global_x.value},{global_y.value},{global_theta.value},{global_mode.value},{global_lane.value}") #testing loop works properly
                global_x.value = i
                global_y.value = i+1
                global_theta.value = i+2
                global_mode.value = b'G'
                global_lane.value = b'B'
                time.sleep(DELAY) # simulating delay between updates
    except KeyboardInterrupt:
        # Set the event to signal all threads to stop
        should_stop.set()