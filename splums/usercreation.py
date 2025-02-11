from datetime import datetime
from main import session
from models.models import users
from events import Event

#*******************************************************************************************
# CREATE NEW USERS
#*******************************************************************************************

def create_user(event: Event):
  
    new_user = users(
        bronco_id = event.data["user_id"],
        name = event.data["name"],
        photo_url = event.data["photo_url"],
        user_type_id = event.data["user_type_id"],
        created_at = event.time_stamp,
        last_updated_at = event.time_stamp,
    )

    try:
        session.add(new_user)
        session.commit()
        print(f"User created successfully with bronco ID: {new_user.bronco_id}")
        return new_user.bronco_id # Return user_id for testing
    except Exception as e:
        session.rollback()
        print(f"Error creating user: {e}")
        return -1

#*******************************************************************************************
# EDIT USERS
#*******************************************************************************************

def edit_user(event: Event):
    updated_user = session.query(users).filter_by(bronco_id = event.data["user_id"]).first()

    if updated_user: # Check if user exists and commit changes
        updated_user.name = event.data["name"]
        updated_user.last_updated_at = event.time_stamp

        session.commit()
        print("User updated successfully.")
        # return 1
    else:
        session.rollback()
        print("user not found. Unable to edit.")
        # return 0

#*******************************************************************************************
# DELETE USERS
#*******************************************************************************************

def delete_user(event: Event):
    deleted_user = session.query(users).filter_by(bronco_id = event.data).first()

    if deleted_user: # Check if user exists and delete
        session.delete(deleted_user)
        session.commit()
        print(f"User with ID {event.data} has been deleted.")
        # return 1
    else:
        session.rollback()
        print(f"User with ID {event.data} not found. Unable to delete.")
        # return 0

# create_user()
# created_user_id = "214151f"
# edit_user(created_user_id, "Edited user!") # should be success