import datetime

class Event:
    def __init__(self, event_type, data):
        self.event_type = event_type
        self.data = data
        self.time_stamp = datetime.datetime.now()


