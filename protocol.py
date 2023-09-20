import socket
from enum import Enum
from time import sleep
from threading import Thread
from multiprocessing import Value, Event

DELAY = 0.1  # seconds
PORT = 12345
OTHER_IP = "192.168.50.201"  # TODO: change this for other robot


class Lane(Enum):
    A = 0
    B = 1
    C = 2


class Mode(Enum):
    L = 0
    G = 1


# Global variable to indicate if threads should stop
stop_protocol = Event()

# global variables for our robot
x = Value("f", 0.0)
y = Value("f", 0.0)
theta = Value("f", 90.0)  # could be 0 to start off with
mode = Value("i", Mode.L.value)  # either L or G. start in loading zone
lane = Value("i", Lane.A.value)  # either A B or C

# global variables for other robot
other_x = Value("f", 0.0)
other_y = Value("f", 0.0)
other_theta = Value("f", 90.0)
other_mode = Value("i", Mode.L.value)
other_lane = Value("i", Lane.A.value)


def encode_data(x, y, theta, mode, lane):
    """Encode the data into a string to send over the network"""
    return f"{x},{y},{theta},{mode},{lane}".encode("utf-8")


def decode_data(data: bytes):
    """Decode the data received from the network"""
    vars = data.decode("utf-8").split(",")

    if len(vars) != 5:
        return None

    return {
        "x": float(vars[0]),  # in meters
        "y": float(vars[1]),  # in meters
        "theta": float(vars[2]),  # in radians
        "mode": int(vars[3]),  # either L or G (see enum for loading or goal values)
        "lane": int(vars[4]),  # either A, B or C (see enum for values)
    }


def update_other_state(data):
    """Update the state of the other robot"""
    other_x.value = data["x"]
    other_y.value = data["y"]
    other_theta.value = data["theta"]
    other_mode.value = data["mode"]
    other_lane.value = data["lane"]


def p_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", PORT))  # "" means accept connections from all addresses
    server_socket.listen(1)

    # accept incoming connection
    client, address = server_socket.accept()
    print(f"INFO: server started at {address[0]} on port {PORT}")

    while not stop_protocol.is_set():
        data = decode_data(client.recv(1024))
        if data is not None:
            update_other_state(data)
            print(f"INFO: data received {data}")

    server_socket.close()
    print("INFO: closed server socket")


def p_client():
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((OTHER_IP, PORT))
            print(f"INFO: client connected successfully to {OTHER_IP} on port {PORT}")
            break
        except Exception as e:
            client_socket.close()
            print(f"ERROR: {e}")
            sleep(1)  # retry connection in 1 second

    while not stop_protocol.is_set():
        try:
            data = encode_data(x.value, y.value, theta.value, mode.value, lane.value)
            client_socket.send(data)
            sleep(DELAY)
        except Exception as e:
            print(f"ERROR: {e}")

    client_socket.close()
    print("INFO: closed client socket")


def _test_state_updates():
    try:
        # Dummy global variables to test this function
        for i in range(10):
            x.value = i
            y.value = i + 1
            theta.value = i + 2
            mode.value = Mode.L.value
            lane.value = Lane.A.value
            sleep(DELAY)

    except KeyboardInterrupt:
        print("WARNING: Keyboard interrupt detected")


if __name__ == "__main__":
    # Create server and client threads
    server_thread = Thread(target=p_server)
    client_thread = Thread(target=p_client)

    # Start threads
    server_thread.start()
    client_thread.start()

    # Test the state updates
    _test_state_updates()

    # Set the event to signal all threads to stop
    stop_protocol.set()

    # Wait for threads to finish
    server_thread.join()
    client_thread.join()

    print("INFO: all threads finished!")
