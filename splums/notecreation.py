from main import session
from models.models import notes
from events import Event

#*******************************************************************************************
# CREATE NEW NOTES
#*******************************************************************************************

def create_note(event: Event):
    
    new_note = notes(
        note=event.data["note"],
        user_id=event.data["user_id"],
        created_by=event.data["created_by"],
        created_at=event.time_stamp,
        last_updated_at=event.time_stamp,
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

def edit_note(event: Event):
    updated_note = session.query(notes).filter_by(note_id=event.data["note_id"]).first()

    if updated_note: # Check if note exists and commit changes
        updated_note.note = event.data["note"]
        updated_note.last_updated_at = event.time_stamp

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

def delete_note(event: Event):
    deleted_note = session.query(notes).filter_by(note_id=event.data).first()

    if deleted_note: # Check if note exists and delete
        session.delete(deleted_note)
        session.commit()
        print(f"Note with ID {event.data} has been deleted.")
        # return 1
    else:
        session.rollback()
        print(f"Note with ID {event.data} not found. Unable to delete.")
        # return 0

# Example test cases
# created_note_id = create_note("Testing for new note!", "att2025", "adm1111")
# edit_note(created_note_id, "Edited note!") # should be success
# delete_note(created_note_id) # should be success

# edit_note(created_note_id, "Edited note!") # should fail
# delete_note(created_note_id) # should fail
