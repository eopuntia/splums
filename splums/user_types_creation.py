

#*******************************************************************************************
# CREATE USER TYPES
#*******************************************************************************************
from datetime import datetime
from main import session
from models.models import user_types


def create_user_type(name: str):
    created_at = datetime.now()
  
    new_user_type = user_types(
        name = name,
    )

    try:
        session.add(new_user_type)
        session.commit()
        print(f"New user type {new_user_type.name} successfully created!")
        return new_user_type.name # Return user_id for testing
    except Exception as e:
        session.rollback()
        print(f"Error creating user type: {e}")
        return -1
    
#*******************************************************************************************
# EDIT USER TYPES
#*******************************************************************************************
    
def edit_user_type(user_type_id: int, user_type: str):
    updated_user_type = session.query(user_types).filter_by(user_type_id =user_type_id).first()

    if updated_user_type: # Check if user exists and commit changes
        updated_user_type.name = user_type
        updated_user_type.last_updated_at = datetime.now()

        session.commit()
        print("User Type updated successfully.")
        # return 1
    else:
        session.rollback()
        print("user Type not found. Unable to edit.")
        # return 0

#*******************************************************************************************
# DELETE USERS
#*******************************************************************************************

def delete_user_type(user_type_id: int):
    deleted_user_type = session.query(user_types).filter_by(user_type_id=user_type_id).first()

    if deleted_user_type: # Check if user exists and delete
        session.delete(deleted_user_type)
        session.commit()
        print(f"User type {user_type_id} has been deleted.")
        # return 1
    else:
        session.rollback()
        print(f"User type {user_type_id} not found. Unable to delete.")
        # return 0

#create_user_type()
#created_user_id = "214151f"
#edit_user(created_user_id, "Edited user!") # should be success

