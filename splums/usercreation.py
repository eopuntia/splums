from datetime import datetime
from main import session
from models.models import users

#*******************************************************************************************
# CREATE NEW USERS
#*******************************************************************************************

def create_user(bronco_id: str, name: str, photo_url: str, user_type_id: int):
    created_at = datetime.now()
  
    new_user = users(
        bronco_id = bronco_id,
        name = name,
        photo_url =photo_url,
       user_type_id = user_type_id,
       created_at = created_at,
        last_updated_at=created_at,
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

def edit_user(bronco_id: int, user: str):
    updated_user = session.query(users).filter_by(bronco_id =bronco_id).first()

    if updated_user: # Check if user exists and commit changes
        updated_user.bronco_id = bronco_id
        updated_user.last_updated_at = datetime.now()

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

def delete_user(bronco_id: int):
    deleted_user = session.query(users).filter_by(bronco_id=bronco_id).first()

    if deleted_user: # Check if user exists and delete
        session.delete(deleted_user)
        session.commit()
        print(f"User with ID {bronco_id} has been deleted.")
        # return 1
    else:
        session.rollback()
        print(f"User with ID {bronco_id} not found. Unable to delete.")
        # return 0

create_user()
created_user_id = "214151f"
edit_user(created_user_id, "Edited user!") # should be success