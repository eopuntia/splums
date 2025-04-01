from events import Event, EventTypes
from sqlalchemy import select
from models.models import Account

def check_if_swiped_in(event, session, event_broker):
    with session.begin() as s:
        account = s.scalar(select(Account).where(Account.win == event.data["win"]))
        if account is None:
            raise KeyError(f"invalid win: {event.data['win']}")

        ret = {}
        if account.swiped_in == 1:
            ret["swiped_in"] = True
        else:
            ret["swiped_in"] = False

        return ret
def swipe_in(event, session, event_broker):
    with session.begin() as s:
        account = s.scalar(select(Account).where(Account.win == event.data["win"]))
        if account is None:
            raise KeyError(f"invalid win: {event.data['win']}")
        else:
            if(account.role.name != "blacklisted"):
                account.swiped_in = 1
                s.commit()
                event_broker.process_event(Event(EventTypes.ACCEPTED_SWIPE_IN, event.data))
            else:
                event_broker.process_event(Event(EventTypes.DENIED_SWIPE_IN, {"name": account.display_name, "status": "blacklisted"}))

def swipe_out(event, session, event_broker):
    with session.begin() as s:
        account = s.scalar(select(Account).where(Account.win == event.data["win"]))
        if account is None:
            raise KeyError(f"invalid win: {event.data['win']}")
        else:
            if(account.role.name != "blacklisted"):
                account.swiped_in = 0
                s.commit()
                event_broker.process_event(Event(EventTypes.ACCEPTED_SWIPE_OUT, event.data))
            else:
                event_broker.process_event(Event(EventTypes.DENIED_SWIPE_OUT, {"name": account.display_name, "role": "blacklisted"}))
