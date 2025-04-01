from events import Event, EventTypes
from sqlalchemy import select,  or_
from models.models import Account, Affiliation, Role, Department

from datetime import datetime
from dateutil.relativedelta import relativedelta


DELETE_USERS_AFTER_YEARS = 10
ARCHIVE_USERS_AFTER_MONTHS = 10

# TODO add proper error handling
def create(event, session):
    with session.begin() as s:
        required_keys = ["given_name", "display_name", "surname", "role", "win"]
        for key in required_keys:
            if key not in event.data:
                raise KeyError(f"Missing required key: {key}")
                
        account_role = s.scalar(select(Role).where(Role.name == event.data["role"]))
        if account_role is None:
            raise KeyError(f"Invalid role: {event.data['role']}")

        account = Account(win = event.data["win"], 
                          role=account_role, 
                          given_name = event.data["given_name"], 
                          surname = event.data["surname"], 
                          display_name = event.data["display_name"], 
                          photo_url = event.data.get("photo_url", "/no/img"))

        s.add(account)
        s.commit()
        return 1

# TODO add proper error handling
def edit(event, session):
    with session.begin() as s:
        required_keys = ["win", "edit_attrs"]
        for key in required_keys:
            if key not in event.data:
                raise KeyError(f"Missing required key: {key}")
                
        account = s.scalar(select(Account).where(Account.win == event.data["win"]))
        if account is None:
            raise KeyError(f"Invalid win: {event.data['win']}")
        for update in event.data["edit_attrs"]:
            if update == "role":
                new_role = s.scalar(select(Role).where(Role.name == event.data["edit_attrs"][update]))
                if new_role is None:
                    raise KeyError(f"Invalid role: {event.data['edit_attrs'][update]}")
                account.role = new_role

            if update == "surname":
                account.surname = event.data["edit_attrs"][update]
            if update == "given_name":
                account.given_name = event.data["edit_attrs"][update]
            if update == "display_name":
                account.display_name = event.data["edit_attrs"][update]
            if update == "photo_url":
                account.photo_url = event.data["edit_attrs"][update]

        s.commit()
        return 1

# TODO add proper error handling
def delete(event, session):
    with session.begin() as s:
        required_keys = ["win"]
        for key in required_keys:
            if key not in event.data:
                raise KeyError(f"Missing required key: {key}")
                
        account = s.scalar(select(Account).where(Account.win == event.data["win"]))
        if account is None:
            raise KeyError(f"err invalid account id: {event.data['win']}")
        
        s.delete(account)
        s.commit()
        return 1
    
#*******************************************************************************************
# ARCHIVE USER
#*******************************************************************************************
# takes win
def archive_user(event: Event, session):
    try:
        with session() as s:
            win = event.data.get('win', None)

            if not win:
                raise ValueError("\033[91mWIN is missing!\033[0m")

            archived_user = s.scalars(select(Account).join(Role).where(Account.win == win))
            archived_type = s.scalars(select(Role).where(Role.name == "archived"))
            archived_user.role_id = archived_type.role_id
            print(f"\033[92mUser with ID {win} Archived.\033[0m")
            s.commit()
    except ValueError as e:
        print(f"\033[91mValue error:\033[0m {e}")
        s.rollback()
    except Exception as e:
        print(f"\033[91mDatabase error:\033[0m {e}")
        s.rollback()
        return -1

#*******************************************************************************************
# AUTO DELETE USERS AFTER 10 YEARS
#*******************************************************************************************
def auto_delete_user(session):
    with session() as s:
        print("Deleting users...")
        archived_users = s.scalars(select(Account).join(Role).where(Role.name == "archived" and Account.last_updated_at <= datetime.now() - relativedelta(years=DELETE_USERS_AFTER_YEARS)))
        for user in archived_users:
            delete(Event(event_type=EventTypes.DELETE_USER, data={'win': user.win}), session)

#*******************************************************************************************
# AUTO ARCHIVE USERS AFTER 10 MONTHS
#*******************************************************************************************
def auto_archive_user(session):
    with session() as s:
        print("Archiving users...")
        users_to_archive = s.scalars(select(Account).join(Role).where((Role.name != "archived" and Account.last_access <= datetime.now() - relativedelta(months=ARCHIVE_USERS_AFTER_MONTHS))))
        for user in users_to_archive:
            archive_user(Event(event_type=EventTypes.ARCHIVE_USER, data={'win': user.win}))

#*******************************************************************************************
# PROMOTE/DEMOTE A USER
#*******************************************************************************************
# Takes win and role.name
def change_user_role(event: Event, session): # Promote or demote a user as an administrator
    try:
        with session() as s:
            win = event.data.get('win', None)

            if not win:
                raise ValueError("\033[91mWIN is missing!\033[0m")
            
            promoted_user = s.scalars(select(Account).where(Account.win == win))

            if promoted_user and 'user_type' in event.data:
                user_type = s.scalars(select(Role).where(Role.name == event.data['name']))
                promoted_user.user_type_id = user_type.user_type_id
                session.commit()
                print(f"\033[92mChanged user_type of user with ID {win} to {event.data['name']}.\033[0m")
            else:
                session.rollback()
                print(f"\033[91mUnable to change user_type of user with ID {win}.\033[0m")
    except KeyError as e:
        print(f"\033[91mMissing key:\033[0m {e}")
    except ValueError as e:
        print(f"\033[91mValue error:\033[0m {e}")
    except Exception as e:
        print(f"\033[91mUnexpected error:\033[0m {e}")


"""
EVENT BROKER USER DATABASE QUERIES
"""

#*******************************************************************************************
# FORMAT REQUESTED USER TO SEND TO SERVER
#*******************************************************************************************
# Takes queried users
def format_users(unformatted_user):
    print("Formatting users...")
    user_dicts = []
    for user in unformatted_user:
        user_dict = {
            'win': user.win,
            'display_name': user.display_name,
            'given_name': user.given_name,
            'surname': user.surname,
            'photo_url': user.photo_url,
            'role': user.role.name,
            'affiliation':user.affiliation.name,
            'created_at': user.created_at,
            'last_updated_at': user.last_updated_at,
            'swiped_in': user.swiped_in,
            'rso': user.rso,
            'last_access': user.last_access
        }
        user_dicts.append(user_dict)
        print(user_dict)
    return user_dicts

#*******************************************************************************************
# GET SWIPED IN USERS
#*******************************************************************************************
# Called by GET_SWIPED_IN_USERS event
def get_swiped_in_users(session):
    try:
        with session() as s:

            requested_users = s.scalars(select(Account).where(Account.swiped_in == True))

            return format_users(requested_users)
    except Exception as e:
        print(f"Error getting signed-in users: {e}")
        return -1
    
#*******************************************************************************************
# GET USERS BY SEARCH FIELDS
#*******************************************************************************************
# Called by GET_USERS_BY_SEARCH event
def search_users(event, session):
    with session() as s:
        query = select(Account).join(Affiliation).join(Role).join(Department)

        filters = []
        name = event.data.get("name")
        affiliation = event.data.get("affiliation")
        role = event.data.get("role")
        department = event.data.get("department")
        rso = event.data.get("rso")

        if name:
            print("Adding name query...")
            filters.append(or_(
                Account.display_name.ilike(f"%{name}%"),
                Account.given_name.ilike(f"%{name}%"),
                Account.surname.ilike(f"%{name}%")
            ))

        if affiliation:
            print("Adding affiliation query...")
            filters.append(Affiliation.name.ilike(f"%{affiliation}%"))

        if role:
            print("Adding role query...")
            filters.append(Role.name.ilike(f"%{role}%"))

        if department:
            print("Adding department query...")
            filters.append(Department.name.ilike(f"%{department}%"))
        if rso:
            print("Adding rso query...")
            filters.append(Account.rso.ilike(f"%{rso}%"))

        if filters:
            query = query.where(*filters)

        results = s.scalars(query).all()
        return format_users(results)