from models.models import Event

# TODO: inlcude active attendant in event log
def log(event, session):
    if  event.data == None or "win" not in event.data:
        win = None
    else:
        win = event.data["win"]
    with session.begin() as s:
        new_event = Event(event_type_id = event.event_type + 1,
                          win = win,
                          occured_at = event.time_stamp)
        s.add(new_event)
        s.commit()
        