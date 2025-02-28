import socket
import pickle

from events import Event
from events import EventTypes

HOST = '127.0.0.1'
PORT = 1000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

print(f"\033[93mStarting client...\033[0m")

# Create test event data
event_data = {
                    'win': '123123123',
                    'name': 'Client Test User'
                }

event = Event(event_type=EventTypes.CREATE_NEW_USER, data=event_data) # Create event to send to server

client.sendall(pickle.dumps(event)) # Send event to server

client.close()
