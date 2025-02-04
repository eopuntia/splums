from events import Event
from events import EventTypes
from main import session
from models.models import users


#*******************************************************************************************
# PROCESS SWIPE IN
#*******************************************************************************************
def swipe_in_process(event: Event):
    from event_broker import event_broker
    """Currently this only checks if the user exists, and is allowed in the shop.
        It does not check if they are currently in the shop as I'm not sure there
        is a way to do that at the moment."""
    user = session.query(users).filter_by(bronco_id=event.data).first()
    if user:    # Check that User exists in DB
        print(f"User, {user.name}, Found!")
        if user.user_type_id != 4:  # Check that user is not blacklisted
            event_broker(Event(EventTypes.ACCEPTED_SWIPE_IN, user))
        else:
            print(f"User, {user.name}, is Blacklisted")
            event_broker(Event(EventTypes.DENIED_SWIPE_IN, user))
    else:
        print(f"User Not Found!")
        event_broker(Event(EventTypes.DENIED_SWIPE_IN, "User Not Found!"))

#*******************************************************************************************
# PROCESS SWIPE OUT
#*******************************************************************************************
def swipe_out_process(event: Event):
    from event_broker import event_broker
    """Currently this only checks if the user exists, and is allowed in the shop.
        It does not check if they are currently in the shop as I'm not sure there
        is a way to do that at the moment."""
    user = session.query(users).filter_by(bronco_id=event.data).first()
    if user:    # Check that User exists in DB
        print(f"User, {user.name}, Found!")
        if user.user_type_id != 4:  # Check that user is not blacklisted
            event_broker(Event(EventTypes.ACCEPTED_SWIPE_OUT, user))
        else:
            print(f"User, {user.name}, is Blacklisted")
            event_broker(Event(EventTypes.DENIED_SWIPE_OUT, user))
    else:
        print(f"User Not Found!")
        event_broker(Event(EventTypes.DENIED_SWIPE_OUT, "User Not Found!"))
