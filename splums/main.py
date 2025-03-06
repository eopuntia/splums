import os
import gui
import sys

from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import scoped_session, sessionmaker
from PyQt6.QtWidgets import QApplication

from event_broker import EventBroker
from events import Event
from events import EventTypes

from models.models import Base

if __name__ == "__main__": 
    engine = create_engine("mariadb+mariadbconnector://splums:example@127.0.0.1:3307/splums")
    Base.metadata.create_all(engine)

    session = sessionmaker(engine)

    event_broker = EventBroker(session)
    
    #event_broker.process_event(Event(EventTypes.SWIPE_IN, {"win": "212222"}))
#    event_broker.process_event(Event(EventTypes.SWIPE_OUT, {"win": "212222"}))

#    event_broker.process_event(Event(EventTypes.CREATE_NOTE, {"text": "THIS IS A TEST NOTE", "subject_account_id": 212222, "creator_account_id": 1234}))

#    event_broker.process_event(Event(EventTypes.EDIT_NOTE, {"note_id": 3, "edit_attrs": {"text": "new_text", "attendent_view_perms": 0}}))

#    event_broker.process_event(Event(EventTypes.DELETE_NOTE, {"note_id": 2}))

#    event_broker.process_event(Event(EventTypes.CREATE_ACCOUNT, {"surname": "lastname", "display_name": "disp_name", "given_name": "given_name", "role": "administrator", "win": 5555}))
    
#    event_broker.process_event(Event(EventTypes.EDIT_ACCOUNT, {"account_id": 212222, "edit_attrs": {"role": "user"}}))

#    event_broker.process_event(Event(EventTypes.DELETE_ACCOUNT, {"account_id": 4321}))

    #Get the GUI started
    splums = QApplication(sys.argv)
    splums.setStyle("Breeze")
    window = gui.MainWindow()
    window.show()
    splums.exec()
