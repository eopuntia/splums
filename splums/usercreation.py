from datetime import datetime, timedelta

from matplotlib.dates import relativedelta
from main import session
from models.models import users
from models.models import user_types
from models.models import event_logs
from models.models import event_types
from sqlalchemy import and_, func as f
from sqlalchemy.exc import SQLAlchemyError
from events import Event

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

def create_user_event(event: Event):
    try:
        required_keys = ["account_id", "role_id", "status_id", "display_name", "given_name", "surname", "photo_url"]
        for key in required_keys:
            if key not in event.data:
                raise KeyError(f"Missing required key: {key}")
        
        account_id = event.data.get('account_id')
        role_id = event.data.get('role_id')
        status_id = event.data.get('status_id')
        display_name = event.data.get('display_name')
        given_name = event.data.get('given_name')
        surname = event.data.get('surname')
        photo_url = event.data.get('photo_url', '')
        created_at = datetime.now()
        last_updated_at = datetime.now()

        new_account = Account(
            account_id=account_id,
            role_id=role_id,
            status_id=status_id,
            display_name=display_name,
            given_name=given_name,
            surname=surname,
            photo_url=photo_url,
            created_at=created_at,
            last_updated_at=last_updated_at
        )

        session.add(new_account)
        session.commit()
        print(f"\033[Account with ID {new_account.account_id} created successfully.\033[0m")
        return new_account.note_id # Return note_id for testing
        
    except SQLAlchemyError as e:
        session.rollback()
        print(f"\033[91mDatabase error:\033[0m {e}")
        return -1
    except KeyError as e:
        print(f"Key error: {e}")
    except Exception as e:
        print(f"\033[91mUnexpected error:\033[0m {e}")

#*******************************************************************************************
# EDIT USERS
#*******************************************************************************************

def edit_user(bronco_id: int, user: str):
    updated_user = session.query(users).filter_by(bronco_id =bronco_id).first()
    #updated_user = session.query(account).filter_by(account_)

    if updated_user: # Check if user exists and commit changes
        updated_user.name = user
        updated_user.last_updated_at = datetime.now()


        session.commit()
        print("User updated successfully.")
        # return 1
    else:
        session.rollback()
        print("user not found. Unable to edit.")
        # return 0

def edit_user_event(event: Event):
    try:
        account_id = event.data.get('account_id', '')

        if not account_id:
             raise ValueError("\033[91mAccount_id is missing!\033[90")

#*******************************************************************************************
# DELETE USERS
#*******************************************************************************************

def delete_user(bronco_id: int):
    deleted_user = session.query(users).filter_by(bronco_id=bronco_id).first()
    #deleted_user = session.query(account).filter_by(account_id=account_id).first()

    if deleted_user: # Check if user exists and delete
        session.delete(deleted_user)
        session.commit()
        print(f"User with ID {bronco_id} has been deleted.")
        # return 1
    else:
        session.rollback()
        print(f"User with ID {bronco_id} not found. Unable to delete.")
        # return 0

#*******************************************************************************************
# GET ARCHIVED USERS
#*******************************************************************************************
def get_archived_users():
    return session.query(event_logs).join(event_types).filter(user_types.name == "archived").all()
    #return session.query(account).join(roles).filter(roles.name == 'archived').all()


#*******************************************************************************************
# AUTO DELETE USERS after 10 years
#*******************************************************************************************
def auto_delete_user():
    archived_users = get_archived_users()
    for user in archived_users:
       if(user.last_updated_at <= datetime.now() - relativedelta(years=10)):
           delete_user(user.bronco_id)
           #delete_user(user.account_id)

#*******************************************************************************************

def get_users_to_archive():

    users_to_archive = session.query(event_logs.user_id, f.max(event_logs.timestamp)).join(event_types).filter(event_types.event_type == "login").group_by(event_logs.user_id).all()
    #users_to_archive = session.query(event.account_id, f.max(event.timestamp)).join(event_type).filter(event_type.name == "login").group_by(event.account_id).all()
    return users_to_archive
   

def archive_user():
    users_to_archive = get_users_to_archive()
    for user in users_to_archive:
        if(user.timestamp <= datetime.now() - relativedelta(months=10)):
            user_to_archive = session.query(users).join(user_types).filter(and_(users.bronco_id == user.user_id and user_types.name != "archived")).first()
           #user_to_archive = session.query(account).join(roles).filter(and_(account.account_id == user.account_id and roles.name != "archived")).first()
            if(user_to_archive):
                user_to_archive.user_type = "archived"
                #user_to_archive.role = "archived"
                session.commit()
                print(f"User with ID {user_to_archive.bronco_id} has been archived")
                #print(f"User with ID {user_to_archive.account_id} has been archived)
            else:
                session.rollback()
                print(f"User with ID {user_to_archive.bronco_id} not found. Unable to archive.")
                 #print(f"User with ID {user_to_archive.account_id} not found. Unable to archive)
   


create_user()
created_user_id = "214151f"
edit_user(created_user_id, "Edited user!") # should be success