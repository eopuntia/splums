from events import Event
from events import EventTypes
from sqlalchemy import select
from models.models import Account, Note, Role

class EventBroker:
    def __init__(self, session):
        self.session = session

    def process_event(self, event):
        match event.event_type:
            case EventTypes.SWIPE_IN: 
                print(f"Swipe In")
                self.swipe_in(event)

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
                self.swipe_out(event)

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
                self.create_account(event)

            case EventTypes.DELETE_ACCOUNT:
                print(f"Delete Account")
                self.delete_account(event)

            case EventTypes.EDIT_ACCOUNT: 
                print(f"Edit Account")
                self.edit_account(event)

            case EventTypes.CREATE_NOTE: 
                print(f"Create Note")
                self.create_note(event)

            case EventTypes.DELETE_NOTE: 
                print(f"Delete Note")
                self.delete_note(event)

            case EventTypes.EDIT_NOTE: 
                print(f"Edit Note")
                self.edit_note(event)

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

    def swipe_in(self, event):
        with self.session.begin() as s:
            account = s.scalar(select(Account).where(Account.account_id ==    event.data["win"]))
            if account is None:
                raise KeyError(f"invalid account_id: {event.data["win"]}")
            else:
                if(account.role.name != "blacklisted"):
                    account.swiped_in = 1
                    s.commit()
                    self.process_event(Event(EventTypes.ACCEPTED_SWIPE_IN, event.data))
                else:
                    self.process_event(Event(EventTypes.DENIED_SWIPE_IN, {"name": account.display_name, "status": "blacklisted"}))

    def swipe_out(self, event):
        with self.session.begin() as s:
            account = s.scalar(select(Account).where(Account.account_id ==    event.data["win"]))
            if account is None:
                raise KeyError(f"invalid account_id: {event.data["win"]}")
            else:
                if(account.role.name != "blacklisted"):
                    account.swiped_in = 0
                    s.commit()
                    self.process_event(Event(EventTypes.ACCEPTED_SWIPE_OUT, event.data))
                else:
                    self.process_event(Event(EventTypes.DENIED_SWIPE_OUT, {"name": account.display_name, "role": "blacklisted"}))


    # TODO add proper error handling
    def create_note(self, event):
        with self.session.begin() as s:
            required_keys = ["text", "subject_account_id", "creator_account_id"]
            for key in required_keys:
                if key not in event.data:
                    raise KeyError(f"Missing required key: {key}")
                    
            creator = s.scalar(select(Account).where(Account.account_id == event.data["creator_account_id"]))
            if creator is None:
                print("err invalid creator id")
                return
            subject = s.scalar(select(Account).where(Account.account_id == event.data["subject_account_id"]))
            if subject is None:
                print(f"err invalid subject id: {event.data["subject_account_id"]}")
                return


            new_note = Note(creator_account=creator, subject_account=subject, text=event.data["text"])
            s.add(new_note)
            s.commit()

    # TODO add proper error handling
    def edit_note(self, event):
        with self.session.begin() as s:
            required_keys = ["text", "note_id"]
            for key in required_keys:
                if key not in event.data:
                    raise KeyError(f"Missing required key: {key}")
                    
            note = s.scalar(select(Note).where(Note.note_id == event.data["note_id"]))
            if note is None:
                raise KeyError(f"err invalid note id: {event.data["note_id"]}")
            
            note.text=event.data["text"]
            s.commit()
    
    # TODO add proper error handling
    def delete_note(self, event):
        with self.session.begin() as s:
            required_keys = ["note_id"]
            for key in required_keys:
                if key not in event.data:
                    raise KeyError(f"Missing required key: {key}")
                    
            note = s.scalar(select(Note).where(Note.note_id == event.data["note_id"]))
            if note is None:
                raise KeyError(f"err invalid note id: {event.data["note_id"]}")
            
            s.delete(note)
            s.commit()
        
    # TODO add proper error handling
    def create_account(self, event):
        with self.session.begin() as s:
            required_keys = ["given_name", "display_name", "surname", "role", "win"]
            for key in required_keys:
                if key not in event.data:
                    raise KeyError(f"Missing required key: {key}")
                    
            account_role = s.scalar(select(Role).where(Role.name == event.data["role"]))
            if account_role is None:
                raise KeyError(f"Invalid role: {role}")

            account = Account(account_id = event.data["win"], role=account_role, given_name = event.data["given_name"], surname = event.data["surname"], display_name = event.data["display_name"], photo_url = event.data.get("photo_url", "/no/img"))
            s.add(account)
            s.commit()

    # TODO add proper error handling
    def edit_account(self, event):
        with self.session.begin() as s:
            required_keys = ["account_id", "edit_attrs"]
            for key in required_keys:
                if key not in event.data:
                    raise KeyError(f"Missing required key: {key}")
                    
            account = s.scalar(select(Account).where(Account.account_id == event.data["account_id"]))
            if account is None:
                raise KeyError(f"Invalid account_id: {event.data["account_id"]}")
            for update in event.data["edit_attrs"]:
                if update == "role":
                    new_role = s.scalar(select(Role).where(Role.name == event.data["edit_attrs"][update]))
                    if new_role is None:
                        raise KeyError(f"Invalid role: {event.data["edit_attrs"][update]}")
                    account.role = new_role

                if update == "surname":
                    account.surname = event.data["edit_attrs"][update]
                if update == "given_name":
                    account.given_name = event.data["edit_attrs"][update]
                if update == "display_name":
                    account.display_name = event.data["edit_attrs"][update]
                if update == "photo_url":
                    account.photo_url = event.data["edit_attrs"][update]

            s.commit()
    
    # TODO add proper error handling
    def delete_account(self, event):
        with self.session.begin() as s:
            required_keys = ["account_id"]
            for key in required_keys:
                if key not in event.data:
                    raise KeyError(f"Missing required key: {key}")
                    
            account = s.scalar(select(Account).where(Account.account_id == event.data["account_id"]))
            if account is None:
                raise KeyError(f"err invalid account id: {event.data["account_id"]}")
            
            s.delete(account)
            s.commit()
