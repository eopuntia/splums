from events import Event
from events import EventTypes
from sqlalchemy import select
import note_events, account_events, swipe_events
from models.models import Account, Note, Role

class EventBroker:
    def __init__(self, session):
        self.session = session

    def process_event(self, event):
        match event.event_type:
            case EventTypes.SWIPE_IN: 
                print(f"Swipe In")
                swipe_events.swipe_in(event, self.session, self)

            # TODO IMPLEMENT
            case EventTypes.ACCEPTED_SWIPE_IN:
                print(f"Accepted Swipe In")
                # towerLightGreen()
                # showAttendantScreen(event)
                # showLabScreen(event)
                # expectEnter()
                
            # TODO IMPLEMENT
            case EventTypes.DENIED_SWIPE_IN:
                print(f"Denied Swipe In")
                # towerLightRed()

            case EventTypes.SWIPE_OUT: 
                print(f"Swipe Out")
                swipe_events.swipe_out(event, self.session, self)

            # TODO IMPLEMENT
            case EventTypes.ACCEPTED_SWIPE_OUT: 
                print(f"Accepted Swipe Out")
                # towerLightGreen()
                # removeAttendantScreen(event)
                # removeLabScreen(event)
                # expectExit()
        
            # TODO IMPLEMENT
            case EventTypes.DENIED_SWIPE_OUT: 
                print(f"Denied Swipe Out")
                # towerLightRed()

            # TODO IMPLEMENT
            case EventTypes.EXPECTED_GATE_CROSSING: 
                print(f"Expected Gate Crossing")

            # TODO IMPLEMENT
            case EventTypes.UNEXPECTED_GATE_CROSSING: 
                print(f"Unexpected Gate Crossing")
                # activateAlarm()
                # towerLightRed()

            case EventTypes.CREATE_ACCOUNT: 
                print(f"Create New Account")
                account_events.create(event, self.session)

            case EventTypes.DELETE_ACCOUNT:
                print(f"Delete Account")
                account_events.delete(event, self.session)

            case EventTypes.EDIT_ACCOUNT: 
                print(f"Edit Account")
                account_events.edit(event, self.session)

            case EventTypes.CREATE_NOTE: 
                print(f"Create Note")
                note_events.create(event, self.session)

            case EventTypes.DELETE_NOTE: 
                print(f"Delete Note")
                note_events.delete(event, self.session)

            case EventTypes.EDIT_NOTE: 
                print(f"Edit Note")
                note_events.edit(event, self.session)

            # TODO IMPLEMENT
            case EventTypes.OPEN_LAB: 
                print(f"Open Lab")
                self.open_lab(event)

            # TODO IMPLEMENT
            case EventTypes.CLOSE_LAB: 
                print(f"Close Lab")
                self.close_lab(event)

            # TODO IMPLEMENT
            case EventTypes.ARCHIVE_ACCOUNT: 
                print(f"Archive User")
                # self.archive_account(event)

            case _:
                print(f"Error")
