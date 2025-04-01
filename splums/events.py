import datetime
from enum import Enum

class Event:
    def __init__(self, event_type, data):
        self.event_type = event_type
        self.data = data
        self.time_stamp = datetime.datetime.now()

class EventTypes(Enum):
    SWIPE_IN = 0
    ACCEPTED_SWIPE_IN = 1
    DENIED_SWIPE_IN = 2
    SWIPE_OUT = 3
    ACCEPTED_SWIPE_OUT = 4
    DENIED_SWIPE_OUT = 5
    EXPECTED_GATE_CROSSING = 6
    UNEXPECTED_GATE_CROSSING = 7
    CREATE_ACCOUNT = 8
    DELETE_ACCOUNT = 9
    EDIT_ACCOUNT = 10
    CREATE_NOTE = 11
    EDIT_NOTE = 12
    DELETE_NOTE = 13
    OPEN_LAB = 14
    CLOSE_LAB = 15
    ARCHIVE_ACCOUNT = 16
    CHANGE_USER_ROLE = 17
    GET_SWIPED_IN_USERS = 18
    GET_NOTES_FOR_USER_ADMIN = 19
    GET_NOTES_FOR_USER_ATTENDANT = 20
    GET_USERS_BY_SEARCH = 21
    
