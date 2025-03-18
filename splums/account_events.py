from events import Event
from sqlalchemy import select
from models.models import Account, Role

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

        account = Account(account_id = event.data["win"], 
                          role=account_role, 
                          given_name = event.data["given_name"], 
                          surname = event.data["surname"], 
                          display_name = event.data["display_name"], 
                          photo_url = event.data.get("photo_url", "/no/img"))

        s.add(account)
        s.commit()

# TODO add proper error handling
def edit(event, session):
    with session.begin() as s:
        required_keys = ["account_id", "edit_attrs"]
        for key in required_keys:
            if key not in event.data:
                raise KeyError(f"Missing required key: {key}")
                
        account = s.scalar(select(Account).where(Account.account_id == event.data["account_id"]))
        if account is None:
            raise KeyError(f"Invalid account_id: {event.data['account_id']}")
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

# TODO add proper error handling
def delete(event, session):
    with session.begin() as s:
        required_keys = ["account_id"]
        for key in required_keys:
            if key not in event.data:
                raise KeyError(f"Missing required key: {key}")
                
        account = s.scalar(select(Account).where(Account.account_id == event.data["account_id"]))
        if account is None:
            raise KeyError(f"err invalid account id: {event.data['account_id']}")
        
        s.delete(account)
        s.commit()

"""
EVENT BROKER USER DATABASE QUERIES
"""

#*******************************************************************************************
# FORMAT REQUESTED USER TO SEND TO SERVER
#*******************************************************************************************
# Takes queried users
def format_users(unformatted_user):
    user_dicts = []
    for user in unformatted_user:
        user_dict = {
            'win': user.account_id,
            'display_name': user.display_name,
            'given_name': user.given_name,
            'surname': user.surname,
            'photo_url': user.photo_url,
            'role': user.role_id,
            'created_at': user.created_at,
            'last_updated_at': user.last_updated_at,
            'swiped_in': user.swiped_in,
            'last_access': user.last_access
        }
        user_dicts.append(user_dict)
    return user_dicts

#*******************************************************************************************
# GET USERS BY REQUESTED ROLE
#*******************************************************************************************
# Takes GET_USERS_BY_ROLE event
def get_users_by_role(event: Event, session):
    try:
        with session() as s:
          role = event.data.get('role', None)

          # strip any leading and trailing spaces/tabs
          if role:
              role = role.strip()
          else:
              role = None

          if not role:
              requested_users = s.scalars(select(Account))
          else:
              requested_users = s.scalars(select(Account).join(Role).where(Role.name == role))

          return format_users(requested_users)
    except Exception as e:
        print(f"Error getting users by role: {e}")
        return -1