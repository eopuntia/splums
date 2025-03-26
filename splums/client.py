import socket
import pickle

from events import Event
from events import EventTypes

HOST = '127.0.0.1'
PORT = 7373

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

print(f"\033[93mStarting client...\033[0m")

# Create test event data
"""
event_data = {
    'win': '123123123',
    'name': 'Client Test User'
}
"""
event_data = {
    'role': '',
}

event = Event(event_type=EventTypes.GET_USERS_BY_ROLE, data=event_data)

client.sendall(pickle.dumps(event))  # Send event to server

# Receive server response
try:
    response = client.recv(4096)
    if response:
        response_data = pickle.loads(response)
        if response_data == 1:
            print(f"\033[92m[SERVER RESPONSE]\033[0m SUCCESS!")  
        elif response_data == -1:
            print(f"\033[92m[SERVER RESPONSE]\033[0m ERROR!")
        elif response_data:
            print(f"\033[92m[SERVER RESPONSE]\033[0m {response_data}")
        else:
            print(f"\033[92m[SERVER RESPONSE]\033[0m NO DATA")
            print(response_data)
        
except:
    print("\033[91m[ERROR] Failed to receive response from server\033[0m")

client.close()
