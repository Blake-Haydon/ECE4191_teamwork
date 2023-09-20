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
# self global variables
our_x = mp.Value("f", 0.0) # probably should be initialised to a purposeful value in loading zone
our_y = mp.Value("f", 0.0) # probably should be initialised to a purposeful value in loading zone
our_theta = mp.Value("f", 90.0) # could be 0 to start off with
our_mode = mp.Value("c", b'L') # either L or G. start in loading zone
our_lane = mp.Value("c", b' ') # either A B or C
# other robot global variables
their_x = mp.Value("f", 0.0) 
their_y = mp.Value("f", 0.0)
their_theta = mp.Value("f", 90.0)
their_mode = mp.Value("c", b'L')
their_lane = mp.Value("c", b' ')

def p_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print("the server is online...")

    client, address = server_socket.accept()
    print(f"connected to {address} on port {PORT}")
    while not should_stop.is_set():
        data = client.recv(1024)
        decoded_data = data.decode("utf-8")
        variables = decoded_data.split(',')

        if variables[0].strip():  # Check if the first element is not an empty string
            try:
                their_x.value = float(variables[0].strip())
                their_y.value = float(variables[1].strip())
                their_theta.value = float(variables[2].strip())
                
                # TODO: fix the b'G' format issue in mode and lane variables to just print out a 'G'. Not sure if issue with how i'm initialising the character
                print(f"Mode = {variables[3]}, Encoded mode = {variables[3].encode('utf-8')[0]}")
                their_mode.value = variables[3].encode("utf-8")[0]
                their_lane.value = variables[4].encode("utf-8")[0]
                print(f"Their values = {their_x.value},{their_y.value},{their_theta.value},{their_mode.value},{their_lane.value}")
            except ValueError:
                print("Error: Could not convert the string to a float.")
        else:
            print("Error: Empty string received.")
    # return their_x, their_y, their_theta, their_mode, their_lane

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

    while not should_stop.is_set():
        try:
            text = f'{our_x.value},{our_y.value},{our_theta.value},{our_mode.value},{our_lane.value}'
            client_socket.send(bytes(text, "UTF-8"))
            sleep(DELAY)
        except Exception as e:
            print("exception 2 handled")
            client_socket.close()
            print(e)  # print the error

# def format_data(x, y, z, ...):
#     return data

if __name__ == "__main__":
    Thread(target=p_server).start()
    Thread(target=p_client).start()
    try:
        while not should_stop.is_set():
            # Dummy global variables to test this function
            for i in range(50):
                print(f"Our values = {our_x.value},{our_y.value},{our_theta.value},{our_mode.value},{our_lane.value}") # testing the values are right
                our_x.value = i
                our_y.value = i+1
                our_theta.value = i+2
                our_mode.value = b'G'
                our_lane.value = b'B'
                time.sleep(DELAY) # simulating delay between updates
    except KeyboardInterrupt:
        print('Keyboard interrupt detected.')
        # Set the event to signal all threads to stop
        should_stop.set()