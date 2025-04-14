import socket
import select
import queue
import pickle

from events import Event
from event_broker import EventBroker

from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import scoped_session, sessionmaker

from models.models import Base

# Server configuration
HOST = '127.0.0.1'
PORT = 7373

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()
server.setblocking(False)

sockets_list = [server]
message_queue = {}

engine = create_engine("mariadb+mariadbconnector://splums:example@127.0.0.1:3307/splums")
Base.metadata.create_all(engine)

session = sessionmaker(engine)

def call_event_broker():

    event_broker = EventBroker(session)

    # Clean up closed sockets from the queue and sockets list
    for client_socket in list(message_queue.keys()):
        if client_socket.fileno() == -1:  # Check if socket is closed
            print(f"[WARNING] Socket for {client_socket.getpeername()} is closed. Removing from queue.")
            del message_queue[client_socket]
            sockets_list.remove(client_socket)

    # Process messages from each remaining open client socket in the queue
    for client_socket in list(message_queue.keys()):
        if client_socket.fileno() == -1:  # Skip already closed sockets (added check for safety)
            continue

        while not message_queue[client_socket].empty():
            client_addr, event = message_queue[client_socket].get()

            if isinstance(event, Event):  # Validate event object
                # Process event and generate a response
                response_data = event_broker.process_event(event)
                # Try to send response to client
                try:
                    if client_socket.fileno() != -1:  # Double-check if socket is still open
                        client_socket.sendall(pickle.dumps(response_data))
                    else:
                        print(f"[ERROR] Socket for {client_addr} is already closed.")
                except:
                    print(f"[ERROR] Failed to send response to {client_addr}")
                    client_socket.close()
                    sockets_list.remove(client_socket)
                    del message_queue[client_socket]
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
            message_queue[client_socket] = queue.Queue()
            print(f"[NEW CONNECTION] {addr} connected.")
        else:
            try:
                data = s.recv(4096)
                if data:
                    event = pickle.loads(data)  # Deserialize the event
                    message_queue[s].put((s.getpeername(), event))
                else:
                    raise ConnectionResetError
            except:
                print(f"[DISCONNECTED] {s.getpeername()}")
                sockets_list.remove(s)
                s.close()
                del message_queue[s]

    call_event_broker()  # Process queue items
