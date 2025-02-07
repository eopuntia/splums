from datetime import datetime
from main import session
from models.models import notes

#*******************************************************************************************
# CREATE NEW NOTES
#*******************************************************************************************

def create_note(note: str, win: str, created_by: str, attendant_view_perms: bool, attendant_edit_perms: bool):
    created_at = datetime.now()
    
    new_note = notes(
        note=note,
        win=win,
        created_by=created_by,
        created_at=created_at,
        last_updated_at=created_at,
        attendant_view_perms=attendant_view_perms,
        attendant_edit_perms=attendant_edit_perms
    )

    try:
        session.add(new_note)
        session.commit()
        print(f"\033[92mNote with ID {new_note.note_id} created successfully.\033[0m")
        return new_note.note_id # Return note_id for testing
    except Exception as e:
        session.rollback()
        print(f"Error creating note: {e}")
        return -1

#*******************************************************************************************
# EDIT NOTES
#*******************************************************************************************

def edit_note(note_id: int, note: str, attendant_view_perms: bool, attendant_edit_perms: bool):
    updated_note = session.query(notes).filter_by(note_id=note_id).first()

    if updated_note: # Check if note exists and commit changes
        updated_note.note = note
        updated_note.last_updated_at = datetime.now()
        updated_note.attendant_view_perms = attendant_view_perms
        updated_note.attendant_edit_perms = attendant_edit_perms

        session.commit()
        print(f"\033[92mNote with ID {note_id} updated successfully.\033[0m")
        # return 1
    else:
        session.rollback()
        print(f"\033[91mNote with ID {note_id} not found. Unable to edit.\033[0m")
        # return 0
        
#*******************************************************************************************
# DELETE NOTES
#*******************************************************************************************

def delete_note(note_id: int):
    deleted_note = session.query(notes).filter_by(note_id=note_id).first()

    if deleted_note: # Check if note exists and delete
        session.delete(deleted_note)
        session.commit()
        print(f"\033[92mNote with ID {note_id} deleted successfully.\033[0m")
        # return 1
    else:
        session.rollback()
        print(f"\033[91mNote with ID {note_id} not found. Unable to delete.\033[0m")
        # return 0

# Example test cases
created_note_id = create_note("Testing for new note!", "444555666", "777888999", True, False)
edit_note(created_note_id, "Edited note!", True, True) # should be success
delete_note(created_note_id) # should be success

edit_note(created_note_id, "Edited note!", True, False) # should fail
delete_note(created_note_id) # should fail
