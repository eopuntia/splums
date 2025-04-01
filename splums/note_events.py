from events import Event
from sqlalchemy import select 
from models.models import Account, Note

# TODO add proper error handling
def create(event, session):
    with session.begin() as s:
        required_keys = ["text", "subject_win", "creator_win"]
        for key in required_keys:
            if key not in event.data:
                raise KeyError(f"Missing required key: {key}")
                
        creator = s.scalar(select(Account).where(Account.win == event.data["creator_win"]))
        if creator is None:
            print("err invalid creator id")
            return -1

        subject = s.scalar(select(Account).where(Account.win == event.data["subject_win"]))
        if subject is None:
            print(f"err invalid subject id: {event.data['subject_win']}")
            return -1

        new_note = Note(creator_account=creator, subject_account=subject, text=event.data["text"])
        s.add(new_note)
        s.commit()
        return 1

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
        return 1

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
        return 1

"""
EVENT BROKER NOTES DATABASE QUERIES
"""

#*******************************************************************************************
# FORMAT REQUESTED NOTES TO SEND TO SERVER
#*******************************************************************************************
# Takes queried notes
def format_notes(unformatted_note):
    note_dicts = []
    for note in unformatted_note:
        note_dict = {
            'note_id': note.note_id,
            'subject_win': note.subject_win,
            'creator_win': note.creator_win,
            'text': note.text,
            'created_at': note.created_at,
            'last_updated_at': note.last_updated_at,
            'attendant_view_perms': note.attendant_view_perms,
            'attendant_edit_perms': note.attendant_edit_perms
        }
        note_dicts.append(note_dict)
    return note_dicts

#*******************************************************************************************
# GET NOTES FOR USER FOR ADMINS
#*******************************************************************************************
# Takes GET_NOTES_FOR_USER event
def get_notes_for_user_admin(event: Event, session):
    try:
        with session() as s:
            win = event.data.get('win', None)

            requested_notes = s.scalars(select(Note).where(Note.subject_win == win))

            return format_notes(requested_notes)
    except Exception as e:
        print(f"Error getting notes for user: {e}")
        return -1

#*******************************************************************************************
# GET NOTES FOR USER FOR ATTENDANTS
#*******************************************************************************************
# Takes GET_NOTES_FOR_USER event
def get_notes_for_user_attendant(event: Event, session):
    try:
        with session() as s:
            win = event.data.get('win', None)

            requested_notes = s.scalars(select(Note).where(Note.subject_win == win and Note.attendant_view_perms == True))

            return format_notes(requested_notes)
    except Exception as e:
        print(f"Error getting notes for user: {e}")
        return -1