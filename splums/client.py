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
"""
add_user_event_data = {
    'win': '123123123',
    'given_name': 'Client Test User',
    'display_name': 'Ive been tested!',
    'surname': 'Tester',
    'role': 'user'
}

role_event_data = {
    'role': '',
}

note_event_data = {
    'win': '212222',
}
"""

event = Event(event_type=EventTypes.GET_USERS_BY_SEARCH, data={"name": "zathras", "affiliation": "staff", "role": "administrator"})
# event1 = Event(event_type=EventTypes.CREATE_ACCOUNT, data=add_user_event_data)
# event2 = Event(event_type=EventTypes.GET_USERS_BY_ROLE, data=role_event_data)
# event3 = Event(event_type=EventTypes.GET_USERS_BY_AFFILIATION, data=event_data)
# event4 = Event(event_type=EventTypes.GET_SWIPED_IN_USERS, data=None)
# event5 = Event(event_type=EventTypes.GET_NOTES_FOR_USER, data=note_event_data)

#*******************************************************************************************
# CALL SERVER SENDING/REQUESTING INFORMATION
#*******************************************************************************************
# Call from GUI, takes event of any type, and returns data if a GET event
def call_server(event: Event):
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
                return response_data
            else:
                print(f"\033[92m[SERVER RESPONSE]\033[0m NO DATA")
            
    except:
        print("\033[91m[ERROR] Failed to receive response from server\033[0m")

# Call this when closing the application to properly close the connection if needed
def close_connection():
    client.close()

call_server(event)
# call_server(event1)
# call_server(event2)
# call_server(event3)
# call_server(event4)
# call_server(event5)
# close_connection()