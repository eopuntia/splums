import socket
import pickle

from events import Event
from events import EventTypes

class client_connection():
    def __init__(self, host, ip): 
        print(f"\033[93mStarting client...\033[0m")

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, ip))

    def call_server(self, event: Event):
        print(f"sending the event {event.data} to the server in client.py")
        self.client.sendall(pickle.dumps(event))  # Send event to server

        # Receive server response
        try:
            response = self.client.recv(4096)
            if response:
                response_data = pickle.loads(response)
                if response_data == 1:
                    print(f"\033[92m[SERVER RESPONSE]\033[0m SUCCESS!")  
                elif response_data == -1:
                    print(f"\033[92m[SERVER RESPONSE]\033[0m ERROR!")
                elif response_data:
                    print(f"in client, response_data is {response_data}")
                    return response_data
                else:
                    print(f"\033[92m[SERVER RESPONSE]\033[0m NO DATA")
                
        except:
            print("\033[91m[ERROR] Failed to receive response from server\033[0m")

    def close_connection(self):
        print(f"\033[93mClosing client...\033[0m")
        self.client.close()

event_data = {
    'win': '212222222',
    'pin': '1234'
    }

event = Event(event_type=EventTypes.CHECK_USER_PIN, data=event_data)

client = client_connection('127.0.0.1', 7373)
client.call_server(event)
client.close_connection()