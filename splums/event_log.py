from models.models import Event, Account
from sqlalchemy import select,  or_

def log(event, session):
    if  event.data == None or "win" not in event.data:
        win = None
    else:
        win = event.data["win"]

    with session.begin() as s:
        attendant = s.scalar(select(Account).where(Account.active_attendant == 1))
        new_event = Event(event_type_id = event.event_type + 1,
                          win = win,
                          active_attendant = attendant.win,
                          occured_at = event.time_stamp)
        s.add(new_event)
        s.commit()
        