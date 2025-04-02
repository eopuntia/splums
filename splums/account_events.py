from events import Event
from sqlalchemy import select, or_
from models.models import Account, Role, Account_Equipment, Equipment, Affiliation

from events import Event, EventTypes

from datetime import datetime
from dateutil.relativedelta import relativedelta


DELETE_USERS_AFTER_YEARS = 10
ARCHIVE_USERS_AFTER_MONTHS = 10

# TODO add proper error handling
def create(event, session):
    with session.begin() as s:
        required_keys = ["win", "edit_attrs"]
        print(f'EVENTDATA: {event.data}')
        for key in required_keys:
            if key not in event.data:
                raise KeyError(f"Missing required key: {key}")
                
        account_role = s.scalar(select(Role).where(Role.name == event.data["edit_attrs"]["role"]))
        if account_role is None:
            raise KeyError(f"Invalid role: {event.data['role']}")

        account_affiliation = s.scalar(select(Affiliation).where(Affiliation.name == event.data["edit_attrs"]["affiliation"]))

        if account_affiliation is None:
            raise KeyError(f"Invalid affiliation: {event.data['affiliation']}")


        account = Account(win = event.data["win"], 
                          role=account_role, 
                          given_name = event.data["edit_attrs"]["given_name"], 
                          surname = event.data["edit_attrs"]["surname"], 
                          display_name = event.data["edit_attrs"]["display_name"], 
                          affiliation = account_affiliation,
                          rso = event.data["edit_attrs"]["rso"],
                          photo_url = event.data.get("photo_url", "./images/" + event.data["win"] + ".jpg"))

        s.add(account)
        s.commit()

    # once created add the permissions
    with session.begin() as s:
        account = s.scalar(select(Account).where(Account.win == event.data["win"]))
        
        for update in event.data["edit_attrs"]:
            if update == "permissions":
                for equip in event.data["edit_attrs"]["permissions"]:
                    add_e = s.scalar(select(Equipment).where(Equipment.name == equip))
                    acc_equip = Account_Equipment(account=account, equipment=add_e, completed_training=True)
                    account.equipments.append(acc_equip)

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
            if update == "affiliation":
                new_affiliation = s.scalar(select(Affiliation).where(Affiliation.name == event.data["edit_attrs"][update]))
                if new_affiliation is None:
                    raise KeyError(f"Invalid affiliation: {event.data['edit_attrs'][update]}")

                account.affiliation = new_affiliation

            if update == "no_permissions":
                for equip in event.data["edit_attrs"]["no_permissions"]:
                    print(f"GOING TO DELETE {equip}")
                    e_del = s.scalar(select(Equipment.equipment_id).where(Equipment.name == equip))
                    if e_del:
                        del_equip = s.scalars(
                            select(Account_Equipment)
                            .where(Account_Equipment.account == account)
                            .where(Account_Equipment.equipment_id == e_del)
                        )
                        for val in del_equip:
                            s.delete(val)
                        
            if update == "permissions":
                for equip in event.data["edit_attrs"]["permissions"]:
                    add_e = s.scalar(select(Equipment).where(Equipment.name == equip))
                    existing_rel = s.scalar(select(Account_Equipment).where(
                        Account_Equipment.account == account,
                        Account_Equipment.equipment == add_e
                    ))
                    if not existing_rel:
                        acc_equip = Account_Equipment(account=account, equipment=add_e, completed_training=True)
                        account.equipments.append(acc_equip)

            if update == "surname":
                account.surname = event.data["edit_attrs"][update]
            if update == "given_name":
                account.given_name = event.data["edit_attrs"][update]
            if update == "display_name":
                account.display_name = event.data["edit_attrs"][update]
            if update == "photo_url":
                account.photo_url = event.data["edit_attrs"][update]
            if update == "rso":
                account.rso = event.data["edit_attrs"][update]

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

def auto_delete_user(session):
    with session() as s:
        print("Deleting users...")
        archived_users = s.scalars(select(Account).join(Role).where(Role.name == "archived" and Account.last_updated_at <= datetime.now() - relativedelta(years=DELETE_USERS_AFTER_YEARS)))
        for user in archived_users:
            delete(Event(event_type=EventTypes.DELETE_USER, data={'win': user.win}), session)

def auto_archive_user(session):
    with session() as s:
        print("Archiving users...")
        users_to_archive = s.scalars(select(Account).join(Role).where((Role.name != "archived" and Account.last_access <= datetime.now() - relativedelta(months=ARCHIVE_USERS_AFTER_MONTHS))))
        for user in users_to_archive:
            archive_user(Event(event_type=EventTypes.ARCHIVE_USER, data={'win': user.win}))

def change_user_type(event: Event, session): # Promote or demote a user as an administrator
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

def format_users(unformatted_user):
    user_dicts = []
    for user in unformatted_user:
        user_dict = {
            'win': user.win,
            'display_name': user.display_name,
            'given_name': user.given_name,
            'surname': user.surname,
            'photo_url': user.photo_url,
            'role': user.role_id,
            'affiliation': user.affiliation_id,
            'rso': user.rso,
            'created_at': user.created_at,
            'last_updated_at': user.last_updated_at,
            'swiped_in': user.swiped_in,
            'last_access': user.last_access
        }
        user_dicts.append(user_dict)
    return user_dicts

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

def get_swiped_in_users(session):
    try:
        with session() as s:

            requested_users = s.scalars(select(Account) .where(Account.swiped_in == True)).order_by(Account.last_access)

            return format_users(requested_users)
    except Exception as e:
        print(f"Error getting signed-in users: {e}")
        return -1

def get_users_paginated_filtered(event, session):
    with session.begin() as s:
        # this is a little scuffed, but first do the entire query to see what the limit is
        query = s.query(Account)

        if event.data["name"] != "ignore":
            query = query.filter(
                        or_(
                Account.display_name.ilike(f"%{event.data['name']}%"),
                Account.surname.ilike(f"%{event.data['name']}%"),
                Account.given_name.ilike(f"%{event.data['name']}%")
                )
            )

        if event.data["privilege"] != "ignore":
            for item in event.data["privilege"]:
                filtered_role = s.scalar(select(Role).where(Role.name == item))
                if filtered_role is None:
                    print("invalid roleAAAA")
                    return -1

                query = query.filter(Account.role != filtered_role)
                print(f"IN FILTERED ROLE {filtered_role.name}")

        if event.data["affiliation"] != "ignore":
            for item in event.data["affiliation"]:
                print("selecting affiliation to keep {item}")
                filtered_affiliation = s.scalar(select(Affiliation).where(Affiliation.name == item))
                if filtered_affiliation is None:
                    print("invalid affiliation")
                    return -1

                query = query.filter(Account.affiliation != filtered_affiliation)
                print(f"IN FILTERED affiliation {filtered_affiliation.name}")

        if event.data["status"] != "ignore":
            if event.data["status"] == "swiped_in":
                query = query.filter(Account.swiped_in == True)
            if event.data["status"] == "blacklisted":
                blacklisted = s.scalar(select(Role).where(Role.name == "blacklisted"))
                query = query.filter(Account.role == blacklisted)
            if event.data["status"] == "archived":
                archived = s.scalar(select(Role).where(Role.name == "archived"))
                query = query.filter(Account.role == archived)

        account_all = query.all()

        print(f'offset calculation at page: {event.data["page_number"]}, and items {event.data["items_per_page"]}')
        accounts = query.order_by(Account.last_access).offset(
                   (event.data["page_number"] -1) * event.data["items_per_page"]
                ).limit(event.data["items_per_page"]).all()
        for acc in accounts:
            print(f"IN GETPAGE {acc.display_name}")
            print(f"{len(accounts)}")

        ret_data = {}
        ret_data["users"] = format_users(accounts)
        ret_data["total_users"] = len(account_all)
        return ret_data

def get_perms_for_user(event, session):
    with session.begin() as s:
        required_keys = ["win"]
        for key in required_keys:
            if key not in event.data:
                raise KeyError(f"Missing required key: {key}")
                
        account = s.scalar(select(Account).where(Account.win == event.data["win"]))
        if account is None:
            raise KeyError(f"Invalid win: {event.data['win']}")

        perms = s.scalars(select(Account_Equipment).where(
            Account_Equipment.account == account
        )).all()
        perm_data = []
        for perm in perms:
            perm_data.append(perm.equipment.name)

        print(f"PERM DATA{perm_data}")
        return perm_data.copy()

# TODO add proper error handling
def check_if_win_exists(event, session):
    with session.begin() as s:
        required_keys = ["win"]
        for key in required_keys:
            if key not in event.data:
                raise KeyError(f"Missing required key: {key}")
                
        account = s.scalar(select(Account).where(Account.win == event.data["win"]))
        if account is None:
            return { "win" : False }
        else: return { "win" : True } 

# TODO add proper error handling
def get_data_for_user(event, session):
    with session.begin() as s:
        required_keys = ["win"]
        for key in required_keys:
            if key not in event.data:
                raise KeyError(f"Missing required key: {key}")
                
        account = s.scalar(select(Account).where(Account.win == event.data["win"]))
        if account is None:
            raise KeyError(f"Invalid win: {event.data['win']}")

        # since this is matched on key we need to keep track of it
        role = account.role.name
        affiliation = account.affiliation.name

        acc_data = account.__dict__
        acc_data.pop('_sa_instance_state')
        # remove the id
        acc_data.pop('role_id')
        acc_data.pop('affiliation_id')
        # add the actual role
        acc_data['role'] = role
        acc_data['affiliation'] = affiliation

        print(f"in get_data_for_user {acc_data}")

        return acc_data.copy()

