from events import Event
from sqlalchemy import select 
from models.models import Account, Note

# TODO add proper error handling
def create(event, session):
    with session.begin() as s:
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
            print(f"err invalid subject id: {event.data['subject_account_id']}")
            return

        new_note = Note(creator_account=creator, subject_account=subject, text=event.data["text"])
        s.add(new_note)
        s.commit()

# TODO add proper error handling
def edit(event, session):
    with session.begin() as s:
        required_keys = ["note_id", "edit_attrs"]
        for key in required_keys:
            if key not in event.data:
                raise KeyError(f"Missing required key: {key}")
                
        note = s.scalar(select(Note).where(Note.note_id == event.data["note_id"]))
        if note is None:
            raise KeyError(f"err invalid note id: {event.data['note_id']}")
        
        for update in event.data["edit_attrs"]:
            if update == "text":
                note.text = event.data["edit_attrs"][update]
            if update == "attendent_view_perms":
                note.attendant_view_perms = event.data["edit_attrs"][update]
            if update == "attendent_edit_perms":
                note.attendant_edit_perms = event.data["edit_attrs"][update]

        s.commit()

# TODO add proper error handling
def delete(event, session):
    with session.begin() as s:
        required_keys = ["note_id"]
        for key in required_keys:
            if key not in event.data:
                raise KeyError(f"Missing required key: {key}")
                
        note = s.scalar(select(Note).where(Note.note_id == event.data["note_id"]))
        if note is None:
            raise KeyError(f"err invalid note id: {event.data['note_id']}")
        
        s.delete(note)
        s.commit()
