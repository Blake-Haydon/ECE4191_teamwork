# Simple State Protocol (SSP)

## Overview

The Simple State Protocol (SSP) is a simple protocol for sending state updates from
one robot to another. The protocol is designed to be simple to implement and
easy to extend.

## Setup

### 1. Set IP

Set the IP of the other robot in the `protocol.py` file.

```python
OTHER_IP = "XXX.XXX.X.X" # PLACE YOUR IP HERE
OTHER_IP = "127.0.0.1" # use this loopback IP address for testing within your own device
```

### 2. Integrate Code

To integrate the protocol into your project you need to copy the following code into your main thread.

```python
# Create server and client threads
t_server = Thread(target=protocol.p_server)
t_client = Thread(target=protocol.p_client)

# Start threads
t_server.start()
t_client.start()

# Set the event to signal all threads to stop
protocol.stop_protocol.set()

# Wait for threads to finish
t_server.join()
t_client.join()
```

And include the following import modules to handle threading and defining the
global variables (including importing the protocol.py file itself):

```python
from threading import Thread
from multiprocessing import Value, Event
import protocol
```

And after updating the global variables for x, y, theta, mode and lane, make sure to set the event:

```python
protocol.event_send_data.set()
```

### 3. Receive State Updates

To test the protocol you can run the `protocol.py` file. This will send 10 state updates to the other robot.

Below is an example of the output from the `protocol.py` file.

```bash
python protocol.py

INFO: client connected successfully to 192.168.50.201 on port 12345
INFO: server started at 192.168.50.201 on port 12345
INFO: data received {'x': 0.0, 'y': 1.0, 'theta': 2.0, 'mode': 0, 'lane': 0}
INFO: data received {'x': 1.0, 'y': 2.0, 'theta': 3.0, 'mode': 0, 'lane': 0}
INFO: data received {'x': 2.0, 'y': 3.0, 'theta': 4.0, 'mode': 0, 'lane': 0}
INFO: data received {'x': 3.0, 'y': 4.0, 'theta': 5.0, 'mode': 0, 'lane': 0}
INFO: data received {'x': 4.0, 'y': 5.0, 'theta': 6.0, 'mode': 0, 'lane': 0}
INFO: data received {'x': 5.0, 'y': 6.0, 'theta': 7.0, 'mode': 0, 'lane': 0}
INFO: data received {'x': 6.0, 'y': 7.0, 'theta': 8.0, 'mode': 0, 'lane': 0}
INFO: data received {'x': 7.0, 'y': 8.0, 'theta': 9.0, 'mode': 0, 'lane': 0}
INFO: data received {'x': 8.0, 'y': 9.0, 'theta': 10.0, 'mode': 0, 'lane': 0}
INFO: data received {'x': 9.0, 'y': 10.0, 'theta': 11.0, 'mode': 0, 'lane': 0}
INFO: closed client socket
INFO: closed server socket
INFO: all threads finished!
```
