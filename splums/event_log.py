import datetime
from models.models import Event, Account, Affiliation, Role, Department
from sqlalchemy import desc, select,  or_

def log(event, session):
    if  event.data == None or "win" not in event.data:
        win = None
    else:
        win = event.data["win"]

    with session.begin() as s:
        attendant = s.scalar(select(Account).where(Account.active_attendant == 1))
        if attendant is None:
            return
        new_event = Event(event_type_id = event.event_type + 1,
                          win = win,
                          active_attendant = attendant.win,
                          occured_at = event.time_stamp)
        s.add(new_event)
        s.commit()
        

#*******************************************************************************************
# FORMAT REQUESTED USER TO SEND TO SERVER
#*******************************************************************************************
# Takes queried users
def format_logs(unformatted_log):
    print("Formatting logs...")
    log_dicts = []
    for log in unformatted_log:
        log_dict = {
            'win': log.win,
            'display_name': log.account.display_name,
            'given_name': log.account.given_name,
            'surname': log.account.surname,
            'role': log.role.name,
            'affiliation':log.affiliation.name,
            'department': log.department.name,
            'rso': log.account.rso,
            'last_access': log.last_access,
            'occured_at': log.occured_at,
            'event_type': log.event_type_id
        }
        log_dicts.append(log_dict)
        print(log_dict)
    return log_dicts

#*******************************************************************************************
# GET LOGS BY REQUESTED FIELDS
#*******************************************************************************************
# Called by GET_LOGS_BY_SEARCH event
def search_logs(event, session):
    with session() as s:
        query = select(Event).join(Account).join(Affiliation).join(Role).join(Department)

        filters = []
        name = event.data.get("name")
        affiliation = event.data.get("affiliation")
        role = event.data.get("role")
        department = event.data.get("department")
        rso = event.data.get("rso")
        date = event.data.get("date")  # Assuming 'date' is passed in YYYY-MM-DD format


        if name:
            print("Adding name filter...")
            filters.append(or_(
                Account.display_name.ilike(f"%{name}%"),
                Account.given_name.ilike(f"%{name}%"),
                Account.surname.ilike(f"%{name}%")
            ))

        if affiliation:
            print("Adding affiliation filter...")
            filters.append(Affiliation.name.ilike(f"%{affiliation}%"))

        if role:
            print("Adding role filter...")
            filters.append(Role.name.ilike(f"%{role}%"))

        if department:
            print("Adding department filter...")
            filters.append(Department.name.ilike(f"%{department}%"))
        if rso:
            print("Adding rso filter...")
            filters.append(Account.rso.ilike(f"%{rso}%"))

                # Filter by specific date if provided
        if specific_date:
            print("Adding date filter...")
            # Convert the provided date string to a datetime object
            try:
                specific_date = datetime.strptime(date, '%Y-%m-%d').date()
                filters.append(Event.occured_at.ilike(f"%{specific_date}%"))
            except ValueError:
                print(f"Invalid date format: {date}. Expected YYYY-MM-DD.")

        if filters:
            query = query.where(*filters)

        # Sort by occurred_at in descending order (most recent first)
        query = query.order_by(desc(Event.occured_at))

        results = s.scalars(query).all()
        return format_logs(results)
