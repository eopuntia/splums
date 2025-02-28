from datetime import datetime
from main import session
from models.models import notes
from events import Event, EventTypes
from sqlalchemy.exc import SQLAlchemyError

#*******************************************************************************************
# CREATE NEW NOTES
#*******************************************************************************************

def create_note(event: Event):
    try:
        # Ensure that essential parameters exist
        required_keys = ['note', 'win', 'created_by']
        for key in required_keys:
            if key not in event.data:
                raise KeyError(f"Missing required key: {key}")

        created_at = datetime.now()
        
        # Assuming 'event.data' is a dictionary containing these fields
        new_note = notes(
            note = event.data.get('note', ''), # Default to empty string if 'note' is missing
            win = event.data.get('win', ''),
            created_by = event.data.get('created_by', ''),
            created_at = created_at,
            last_updated_at = created_at,
            attendant_view_perms = event.data.get('attendant_view_perms', False),
            attendant_edit_perms = event.data.get('attendant_edit_perms', False)
        )


        session.add(new_note)
        session.commit()
        print(f"\033[92mNote with ID {new_note.note_id} created successfully.\033[0m")
        return new_note.note_id # Return note_id for testing
        
    except SQLAlchemyError as e:
        print(f"\033[91mDatabase error:\033[0m {e}")
        session.rollback()
        return -1
    except KeyError as e:
        print(f"Key error: {e}")
        session.rollback()
    except Exception as e:
        print(f"\033[91mUnexpected error:\033[0m {e}")
        session.rollback()

#*******************************************************************************************
# EDIT NOTES
#*******************************************************************************************

def edit_note(event: Event):
    try:
        note_id = event.data.get('note_id', None)

        # Check that note_id exists
        if not note_id:
                raise ValueError("\033[91mNote_id is missing!\033[90")
        
        updated_note = session.query(notes).filter_by(note_id=note_id).first()

        if updated_note: # Check if note exists and commit changes
            if 'note' in event.data:
                updated_note.note = event.data['note']
            if 'attendant_view_perms' in event.data:
                updated_note.attendant_view_perms = event.data['attendant_view_perms']
            if 'attendant_edit_perms' in event.data:
                updated_note.attendant_edit_perms = event.data['attendant_edit_perms']

            updated_note.last_updated_at = datetime.now()
            
            session.commit()
            print(f"\033[92mNote with ID {note_id} updated successfully.\033[0m")
        else:
            session.rollback()
            print(f"\033[91mNote with ID {note_id} not found. Unable to edit.\033[0m")

    except KeyError as e:
        print(f"\033[91mMissing key:\033[0m {e}")
        session.rollback()
    except ValueError as e:
        print(f"\033[91mValue error:\033[0m {e}")
        session.rollback()
    except Exception as e:
        print(f"\033[91mUnexpected error:\033[0m {e}")
        session.rollback()
        
#*******************************************************************************************
# DELETE NOTES
#*******************************************************************************************

def delete_note(event: Event):
    try:
        note_id = event.data.get('note_id', '')

        if not note_id:
                raise ValueError("\033[91mNote_id is missing!\033[90")

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
            
    except KeyError as e:
        print(f"Missing key: {e}")
        session.rollback()
    except ValueError as e:
        print(f"Value error: {e}")
        session.rollback()
    except Exception as e:
        print(f"Unexpected error: {e}")
        session.rollback()

#*******************************************************************************************
# TESTING EXAMPLES
#*******************************************************************************************

def test_note():
    # Creating mock event data
    create_note_event_data = {
        'note': 'This is a test note',
        'win': '111222333',
        'created_by': '777888999',
        'attendant_view_perms': True,
        'attendant_edit_perms': False
    }

    # Creating an Event instance with test data
    create_event = Event(event_type=EventTypes.CREATE_NOTE, data=create_note_event_data)

    # Calling function with event
    created_note_id = create_note(create_event)

    edit_note_event_data = {
        'note_id': created_note_id,
        'note': 'Edited note!',
        'attendant_view_perms': True,
        'attendant_edit_perms': True
    }

    edit_event = Event(event_type=EventTypes.EDIT_NOTE, data=edit_note_event_data)
    edit_note(edit_event) # should be success

    delete_note_event_data = {
        'note_id': created_note_id,
    }

    delete_event = Event(event_type=EventTypes.DELETE_NOTE, data=delete_note_event_data)
    delete_note(delete_event) # should be success

# test_note()