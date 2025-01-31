from datetime import datetime
# from main import session
from models.models import notes

import sqlalchemy as sa
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import scoped_session, sessionmaker
engine = sa.create_engine("mariadb+mariadbconnector://splums:example@127.0.0.1:3307/splums")
session = scoped_session(
    sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine
    )
)


def create_note(note: str, user_id: str, created_by: str) -> None:
    created_at = datetime.now()
    
    new_note = notes(
        note=note,
        user_id=user_id,
        created_by=created_by,
        created_at=created_at,
        last_updated_at=created_at,
    )

    session.add(new_note)
    session.commit()

    try:
        session.add(new_note)
        session.commit()
        print(f"Note created successfully with ID: {new_note.note_id}")
    except Exception as e:
        session.rollback()
        print(f"Error creating note: {e}")

def edit_note(note_id: int, note: str, user_id: str) -> None:
    updated_note = session.query(notes).filter_by(note_id=note_id).first()

    if updated_note:
        updated_note.note = note
        updated_note.user_id = user_id
        updated_note.last_updated_at = datetime.now()

        session.commit()
        print("Note updated successfully.")
    else:
        print("Note not found.")


create_note("Testing for new note!", "att2025", "adm1111")
