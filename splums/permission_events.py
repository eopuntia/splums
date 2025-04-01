from events import Event, EventTypes
from sqlalchemy import select
from models.models import Equipment

def get_all_perms(event, session):
    with session.begin() as s:
        perms = s.scalars(select(Equipment)).all()
        
        perm_list = []

        for p in perms:
            perm_list.append(p.name)

        return perm_list.copy()
