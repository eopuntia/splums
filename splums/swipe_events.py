from events import Event, EventTypes
from sqlalchemy import select
from models.models import Account

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

def auto_swipe_outs(session, event_broker):
    with session.begin() as s:
        swipe_outs = s.scalars(select(Account).where(Account.swiped_in != 0)).all()
        for user in swipe_outs:
            event_broker.process_event(Event(EventTypes.SWIPE_OUT, {"win": user.win}))