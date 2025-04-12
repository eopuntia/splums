from client import *
from events import *

if __name__ == "__main__":
    client = client_connection("127.0.0.1", 7373)
    event_data = {}
    event_data["win"] = 111111111
    event_data["pin"] = 1111
    event = Event(event_type=EventTypes.SET_USER_PIN, data=event_data)
    client.call_server(event)
