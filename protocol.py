import socket
from enum import Enum
from time import sleep
from threading import Thread
from multiprocessing import Value, Event


class Lane(Enum):
    A = 0
    B = 1
    C = 2


class Mode(Enum):
    L = 0
    G = 1


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
    global_other_x.value = data["x"]
    global_other_y.value = data["y"]
    global_other_theta.value = data["theta"]
    global_other_mode.value = data["mode"]
    global_other_lane.value = data["lane"]


def server(event_stop_protocol, port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", port))  # "" means accept connections from all addresses
    server_socket.listen(1)

    # accept incoming connection
    client, address = server_socket.accept()
    print(f"INFO: server started at {address[0]} on port {port}")

    while not event_stop_protocol.is_set():
        data = decode_data(client.recv(1024))
        if data is not None:
            update_other_state(data)
            print(f"INFO: data received {data}")

    server_socket.close()
    print("INFO: closed server socket")


def client(event_stop_protocol, event_send_data, ip, port=12345):
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((ip, port))
            print(f"INFO: client connected successfully to {ip} on port {port}")
            break
        except Exception as e:
            client_socket.close()
            print(f"ERROR: {e}")
            sleep(1)  # retry connection in 1 second

    while not event_stop_protocol.is_set():
        try:
            data = encode_data(
                global_x.value,
                global_y.value,
                global_theta.value,
                global_mode.value,
                global_lane.value,
            )
            client_socket.send(data)
        except Exception as e:
            print(f"ERROR: {e}")

        event_send_data.clear()
        event_send_data.wait()  # wait for new data to be available

    client_socket.close()
    print("INFO: closed client socket")


if __name__ == "__main__":
    OTHER_IP = "192.168.50.201"  # TODO: change this for other robot!

    event_send_data = Event()  # Global variable to indicate new data is available
    event_stop_protocol = Event()  # Global variable to indicate if threads should stop

    def _test_state_updates():
        try:
            # Dummy global variables to test this function
            for i in range(10):
                global_x.value = i
                global_y.value = i + 1
                global_theta.value = i + 2
                global_mode.value = Mode.L.value
                global_lane.value = Lane.A.value
                event_send_data.set()
                sleep(0.1)

        except KeyboardInterrupt:
            print("WARNING: Keyboard interrupt detected")

    # global variables for our robot
    global_x = Value("f", 0.0)
    global_y = Value("f", 0.0)
    global_theta = Value("f", 90.0)  # could be 0 to start off with
    global_mode = Value("i", Mode.L.value)  # either L or G. start in loading zone
    global_lane = Value("i", Lane.A.value)  # either A B or C

    # global variables for other robot
    global_other_x = Value("f", 0.0)
    global_other_y = Value("f", 0.0)
    global_other_theta = Value("f", 90.0)
    global_other_mode = Value("i", Mode.L.value)
    global_other_lane = Value("i", Lane.A.value)

    # Create server and client threads
    t_server = Thread(target=server, args=(event_stop_protocol,))
    t_client = Thread(
        target=client,
        args=(event_stop_protocol, event_send_data, OTHER_IP),
    )

    # !!!!!!!!!! START THREADS !!!!!!!!!!

    # Start threads
    t_server.start()
    t_client.start()

    # Test the state updates
    _test_state_updates()

    # Set the event to signal all threads to stop
    event_stop_protocol.set()
    event_send_data.set()  # wake up client thread to finish (this is not the best but it works)

    # Wait for threads to finish
    t_server.join()
    t_client.join()

    print("INFO: all threads finished!")
