import datetime
from enum import IntEnum

class Event:
    def __init__(self, event_type, data = None):
        self.event_type = event_type
        self.data = data
        self.time_stamp = datetime.datetime.now()

class EventTypes(IntEnum):
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
    ATTEMPT_ATTENDANT_SIGNIN = 17
    ATTEMPT_ATTENDANT_SIGNOUT = 18
    GET_USERS_BY_ROLE = 19
    GET_USERS_BY_AFFILIATION = 20
    GET_SWIPED_IN_USERS = 21
    GET_NOTE_FOR_USER = 22
    GET_DATA_FOR_USER = 23
    GET_PERMS_FOR_USER = 24
    CHECK_IF_WIN_EXISTS = 25
    GET_ALL_PERMS = 26
    GET_USERS_PAGINATED_FILTERED = 27
    CHECK_IF_SWIPED_IN = 28
    CHANGE_USER_ROLE = 29
    GET_NOTES_FOR_USER_ADMIN = 30
    GET_NOTES_FOR_USER_ATTENDANT = 31
    GET_USERS_BY_SEARCH = 32
    EDIT_NOTE_FOR_USER = 33
    CHECK_IF_ACTIVE_ATTENDANT = 34
    
