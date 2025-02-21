from datetime import datetime

from dateutil.relativedelta import relativedelta
from main import session
from models.models import users, user_types
from sqlalchemy import and_, func as f
from sqlalchemy.exc import SQLAlchemyError
from events import Event, EventTypes

DELETE_USERS_AFTER_YEARS = 10
ARCHIVE_USERS_AFTER_MONTHS = 10

#*******************************************************************************************
# CREATE NEW USERS
#*******************************************************************************************
# takes win and name, and optionally photo_url
def create_user(event: Event):
    try:
        user_type = session.query(user_types).filter(user_types.user_type == "User").first()
        created_at = datetime.now()
    
        new_user = users(
            win = event.data['win'], # Throws error if missing win
            name = event.data['name'],
            photo_url =event.data.get('photo_url', 'None'),
            user_type_id = user_type.user_type_id, # Ensures that a new user is only a user. Can promote later
            created_at = created_at,
            last_updated_at = created_at,
            swiped_in = False,
            last_access = created_at
        )

        session.add(new_user)
        session.commit()
        print(f"\033[92mUser with ID {event.data['win']} created successfully.\033[0m")

        #return new_user.win # Return win for testing
        
    except SQLAlchemyError as e:
        print(f"\033[91mDatabase error:\033[0m {e}")
        session.rollback()
        return -1
    except KeyError as e:
        print(f"Key error: {e}")
    except Exception as e:
        print(f"\033[91mUnexpected error:\033[0m {e}")

#*******************************************************************************************
# EDIT USERS
#*******************************************************************************************
# takes win, and optionally name and photo_url
def edit_user(event: Event):
    try:
        win = event.data.get('win', None)

        if not win:
            raise ValueError("\033[91mWIN is missing!\033[0m")
        
        updated_user = session.query(users).filter(users.win == win).first()

        if updated_user: # Check if user exists and commit changes
            if 'name' in event.data:
                updated_user.name = event.data['name']
            if 'photo_url' in event.data:
                updated_user.photo_url = event.data['photo_url']

            updated_user.last_updated_at = datetime.now()

            session.commit()
            print(f"\033[92mUser with ID {win} updated successfully.\033[0m")
        else:
            session.rollback()
            print(f"\033[91mUser with ID {win} not found. Unable to edit.\033[0m")
        
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
# DELETE USERS
#*******************************************************************************************
# takes win
def delete_user(event: Event):
    try:
        win = event.data.get('win', None)

        if not win:
            raise ValueError("\033[91mWIN is missing!\033[0m")

        deleted_user = session.query(users).filter(users.win == win).first()

        if deleted_user: # Check if user exists and delete
            session.delete(deleted_user)
            session.commit()
            print(f"\033[92mUser with ID {win} has been deleted.\033[0m")
        else:
            session.rollback()
            print(f"\033[91mUser with ID {win} not found. Unable to delete.\033[0m")
    except ValueError as e:
        print(f"\033[91mValue error:\033[0m {e}")
        session.rollback()
    except SQLAlchemyError as e:
        print(f"\033[91mDatabase error:\033[0m {e}")
        session.rollback()
        return -1

#*******************************************************************************************
# ARCHIVE USER
#*******************************************************************************************
# takes win
def archive_user(event: Event):
    try:
        win = event.data.get('win', None)

        if not win:
            raise ValueError("\033[91mWIN is missing!\033[0m")

        archived_user = session.query(users).join(user_types).filter(users.win == win).first()
        archived_type = session.query(user_types).filter(user_types.user_type == "Archived").first()
        archived_user.user_type = archived_type
        archived_user.last_updated_at = datetime.now()
        print(f"\033[92mUser with ID {win} Archived.\033[0m")
        session.commit()
    except ValueError as e:
        print(f"\033[91mValue error:\033[0m {e}")
        session.rollback()
    except SQLAlchemyError as e:
        print(f"\033[91mDatabase error:\033[0m {e}")
        session.rollback()
        return -1

#*******************************************************************************************
# AUTO DELETE USERS AFTER 10 YEARS
#*******************************************************************************************
def auto_delete_user():
    print("Deleting users...")
    archived_users = session.query(users).join(user_types).filter(and_(user_types.user_type == "Archived", users.last_updated_at <= datetime.now() - relativedelta(years=DELETE_USERS_AFTER_YEARS))).all()
    for user in archived_users:
        delete_user(Event(event_type=EventTypes.DELETE_USER, data={'win': user.win}))

#*******************************************************************************************
# AUTO ARCHIVE USERS AFTER 10 MONTHS
#*******************************************************************************************
def auto_archive_user():
    print("Archiving users...")
    users_to_archive = session.query(users).join(user_types).filter(and_(user_types.user_type != "Archived", users.last_access <= datetime.now() - relativedelta(months=ARCHIVE_USERS_AFTER_MONTHS))).all()
    for user in users_to_archive:
        archive_user(Event(event_type=EventTypes.ARCHIVE_USER, data={'win': user.win}))

#*******************************************************************************************
# PROMOTE/DEMOTE A USER
#*******************************************************************************************
# Takes win and user_type
def change_user_type(event: Event): # Promote or demote a user as an administrator
    try:
        win = event.data.get('win', None)

        if not win:
            raise ValueError("\033[91mWIN is missing!\033[0m")
        
        promoted_user = session.query(users).filter_by(win=win).first()

        if promoted_user and 'user_type' in event.data:
            user_type = session.query(user_types).filter(user_types.user_type == event.data['user_type']).first()
            promoted_user.user_type_id = user_type.user_type_id
            session.commit()
            print(f"\033[92mChanged user_type of user with ID {win} to {event.data['user_type']}.\033[0m")
        else:
            session.rollback()
            print(f"\033[91mUnable to change user_type of user with ID {win}.\033[0m")
    except KeyError as e:
        print(f"\033[91mMissing key:\033[0m {e}")
    except ValueError as e:
        print(f"\033[91mValue error:\033[0m {e}")
    except Exception as e:
        print(f"\033[91mUnexpected error:\033[0m {e}")

#*******************************************************************************************
# TESTING EXAMPLES
#*******************************************************************************************

def test_user():
    loop = True
    while(loop):
        print("Choose an option:")
        print("0: exit")
        print("1: create user")
        print("2: edit user")
        print("3: promote user")
        print("4: archive user")
        print("5: delete user")
        print("6: auto archive/delete")
        choice = int(input())
        match choice:
            case 0:
                print("Exiting...")
                loop = False
            case 1:
                # Creating mock event data
                create_user_event_data = {
                    'win': '123123123',
                    'name': 'New Test User'
                }

                # Creating an Event instance with test data
                create_event = Event(event_type=EventTypes.CREATE_NEW_USER, data=create_user_event_data)
                create_user(create_event)

            case 2:
                # Creating mock event data
                edit_user_event_data = {
                    'win': '123123123',
                    'name': 'Newly Edited Test User',
                    'photo_url': 'url'
                }

                edit_event = Event(event_type=EventTypes.EDIT_USER, data=edit_user_event_data)
                edit_user(edit_event)

            case 3:
                # Creating mock event data
                promote_user_event_data = {
                    'win': '123123123',
                    'user_type': 'Attendant'
                }

                promote_event = Event(event_type=EventTypes.ARCHIVE_USER, data=promote_user_event_data)
                change_user_type(promote_event)

            case 4:
                # Creating mock event data
                archive_user_event_data = {
                    'win': '123123123'
                }

                archive_event = Event(event_type=EventTypes.ARCHIVE_USER, data=archive_user_event_data)
                archive_user(archive_event)

            case 5:
                # Creating mock event data
                delete_user_event_data = {
                    'win': '123123123'
                }

                delete_event = Event(event_type=EventTypes.DELETE_USER, data=delete_user_event_data)
                delete_user(delete_event)
            case 6:
                auto_archive_user()
                auto_delete_user()
        

test_user()