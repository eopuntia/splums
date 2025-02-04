from datetime import datetime
from main import session
from models.models import notes

#*******************************************************************************************
# CREATE NEW NOTES
#*******************************************************************************************

def create_note(note: str, user_id: str, created_by: str):
    created_at = datetime.now()
    
    new_note = notes(
        note=note,
        user_id=user_id,
        created_by=created_by,
        created_at=created_at,
        last_updated_at=created_at,
    )

    try:
        session.add(new_note)
        session.commit()
        print(f"Note created successfully with ID: {new_note.note_id}")
        return new_note.note_id # Return note_id for testing
    except Exception as e:
        session.rollback()
        print(f"Error creating note: {e}")
        return -1

#*******************************************************************************************
# EDIT NOTES
#*******************************************************************************************

def edit_note(note_id: int, note: str):
    updated_note = session.query(notes).filter_by(note_id=note_id).first()

    if updated_note: # Check if note exists and commit changes
        updated_note.note = note
        updated_note.last_updated_at = datetime.now()

        session.commit()
        print("Note updated successfully.")
        # return 1
    else:
        session.rollback()
        print("Note not found. Unable to edit.")
        # return 0
        
#*******************************************************************************************
# DELETE NOTES
#*******************************************************************************************

def delete_note(note_id: int):
    deleted_note = session.query(notes).filter_by(note_id=note_id).first()

    if deleted_note: # Check if note exists and delete
        session.delete(deleted_note)
        session.commit()
        print(f"Note with ID {note_id} has been deleted.")
        # return 1
    else:
        session.rollback()
        print(f"Note with ID {note_id} not found. Unable to delete.")
        # return 0

# Example test cases
created_note_id = create_note("Testing for new note!", "att2025", "adm1111")
edit_note(created_note_id, "Edited note!") # should be success
delete_note(created_note_id) # should be success

edit_note(created_note_id, "Edited note!") # should fail
delete_note(created_note_id) # should fail
