import socket
import select
import queue
import pickle

from events import Event  # Import the Event class
from event_broker import event_broker

# Server configuration
HOST = '127.0.0.1'
PORT = 1000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()
server.setblocking(False)

sockets_list = [server]
message_queue = queue.Queue()

def call_event_broker():
     # Processes messages from the queue one at a time.
    while not message_queue.empty():
        client_addr, event = message_queue.get()
        if isinstance(event, Event):  # Validate that it's an Event object
            print(f"[EVENT BROKER] Processing Event from {client_addr}: {event.event_type} - {event.data}")
            event_broker(event)
        else:
            print(f"[WARNING] Received invalid data from {client_addr}")

print(f"[LISTENING] Server is running on {HOST}:{PORT}")

while True:
    readable, _, errored = select.select(sockets_list, [], sockets_list)

    for s in readable:
        if s is server:
            client_socket, addr = server.accept()
            client_socket.setblocking(False)
            sockets_list.append(client_socket)
            print(f"[NEW CONNECTION] {addr} connected.")
        else:
            try:
                data = s.recv(4096)
                if data:
                    event = pickle.loads(data)  # Deserialize the event
                    print(f"[{s.getpeername()}] Queued Event: {event.event_type}")
                    message_queue.put((s.getpeername(), event))
                else:
                    raise ConnectionResetError
            except:
                print(f"[DISCONNECTED] {s.getpeername()}")
                sockets_list.remove(s)
                s.close()

    call_event_broker()  # Process queue one item at a time
