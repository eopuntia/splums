import csv # For reading DB information

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import Column, Integer, VARCHAR, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Relationship

engine = sa.create_engine("mariadb+mariadbconnector://splums:example@127.0.0.1:3307/splums")
connect = engine.connect()

metadata = sa.MetaData()

#*******************************************************************************************
# CREATE DB TABLES
#*******************************************************************************************

# Create users table
users_table = sa.Table(
    "users", 
    metadata,
    Column("bronco_id", VARCHAR(255), primary_key=True),
    Column("name", VARCHAR(255), nullable=False),
    Column("photo_url", VARCHAR(255), nullable=False),
    Column("user_type_id", Integer, ForeignKey("user_types.user_type_id", ondelete="CASCADE"), nullable=False, index=True, unique=True),
    Column("created_at", DateTime, nullable=False, default=datetime.now),
    Column("last_updated_at", DateTime, nullable=False, default=datetime.now)
)

# Create user_types table
user_types_table = sa.Table(
    "user_types", 
    metadata,
    Column("user_type_id", Integer, primary_key=True, autoincrement=True),
    Column("user_type", VARCHAR(255), nullable=False)
)

# Create notes table
notes_table = sa.Table(
    "notes",
    metadata,
    Column("note_id", Integer, primary_key=True, autoincrement=True),
    Column("note", VARCHAR(255), nullable=False),
    Column("user_id", VARCHAR(255), ForeignKey("users.bronco_id", ondelete="CASCADE"), nullable=False, index=True, unique=True),
    Column("created_by", VARCHAR(255), ForeignKey("users.bronco_id", ondelete="CASCADE"), nullable=False, index=True, unique=True),
    Column("created_at", DateTime, nullable=False, default=datetime.now),
    Column("last_updated_at", DateTime, nullable=False, default=datetime.now)
)

# Create user_machines table
user_machines_table = sa.Table(
    "user_machines",
    metadata,
    Column("user_machines_id", Integer, primary_key=True, autoincrement=True),
    Column("equipment_id", Integer, ForeignKey("equipment.equipment_id", ondelete="CASCADE"), nullable=False, index=True, unique=True),
    Column("completed_training", Boolean, nullable=False, default=False),
    Column("user_id", VARCHAR(255), ForeignKey("users.bronco_id", ondelete="CASCADE"), nullable=False, index=True),
)

# Create equipment table
equipment_table = sa.Table(
    "equipment",
    metadata,
    Column("equipment_id", Integer, primary_key=True, autoincrement=True),
    Column("equipment_name", VARCHAR(255), nullable=False)
)

# Create event_logs table
event_logs_table = sa.Table(
    "event_logs",
    metadata,
    Column("event_id", Integer, primary_key=True, autoincrement=True),
    Column("event_type_id", Integer, ForeignKey("event_types.event_types_id", ondelete="CASCADE"), nullable=False, index=True),
    Column("user_id", VARCHAR(255), ForeignKey("users.bronco_id", ondelete="CASCADE"), nullable=False, index=True),
    Column("timestamp", DateTime, nullable=False, default=datetime.now)
)

# Create event_types table
event_types_table = sa.Table(
    "event_types",
    metadata,
    Column("event_types_id", Integer, primary_key=True, autoincrement=True),
    Column("event_type", VARCHAR(255), nullable=False)
)

#*******************************************************************************************
# INSERT DB INFO
#*******************************************************************************************

# Inserts user information intp users table
def insert_user(bronco_id: str, name: str, photo_url: str, user_type_id: int, created_at: datetime, last_updated_at: datetime) -> None:
    with engine.connect() as conn:
        query = users_table.insert().values(
            bronco_id=bronco_id, 
            name=name, 
            photo_url=photo_url, 
            user_type_id=user_type_id, 
            created_at=created_at, 
            last_updated_at=last_updated_at
        )
        conn.execute(query)

# Inserts user types into user_types table
def insert_user_types(user_type: str) -> None:
    with engine.connect() as conn:
        query = user_types_table.insert().values(user_type=user_type)
        conn.execute(query)

# Inserts notes into notes table
def insert_notes(note: str, user_id: str, created_by: str, created_at: datetime, last_updated_at: datetime) -> None:
    with engine.connect() as conn:
        query = notes_table.insert().values(
            note=note,
            user_id=user_id,
            created_by=created_by,
            created_at=created_at,
            last_updated_at=last_updated_at
        )
        conn.execute(query)

# Inserts user machines into user_machines table
def insert_user_machines(equipment_id: int, completed_training: bool, user_id: str) -> None:
    with engine.connect() as conn:
        query = user_machines_table.insert().values(
            equipment_id=equipment_id,
            completed_training=completed_training,
            user_id=user_id
        )
        conn.execute(query)

# Inserts equipment into equipment table
def Insert_equipment(equipment_name: str) -> None:
    with engine.connect() as conn:
        query = equipment_table.insert().values(equipment_name=equipment_name)
        conn.execute(query) 

# Inserts new event log into event_log table
def Insert_event_log(event_type_id: int, user_id: str, timestamp: datetime) -> None:
    with engine.connect() as conn:
        query = event_logs_table.insert().values(
            event_type_id=event_type_id,
            user_id=user_id,
            timestamp=timestamp
        )
        conn.execute(query) 

# Inserts event type into event_type table
def Insert_event_type(event_type: str) -> None:
    with engine.connect() as conn:
        query = event_types_table.insert().values(event_type=event_type)
        conn.execute(query)

#*******************************************************************************************
# READ DB INFO
#*******************************************************************************************


def Read_users() -> None:
    with open('db_info/users.csv') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            bronco_id = row[0].strip()  # Strip any extra whitespace
            name = row[1].strip()
            photo_url = row[2].strip()
            user_type_id = int(row[3].strip())  # Convert user_type_id to integer and strip extra spaces
            created_at = datetime.strptime(row[4].strip(), "%Y-%m-%d %H:%M:%S")  # Convert to datetime and strip spaces
            last_updated_at = datetime.strptime(row[5].strip(), "%Y-%m-%d %H:%M:%S")

            # Insert each user
            insert_user(bronco_id, name, photo_url, user_type_id, created_at, last_updated_at)


def Read_user_types() -> None:
    with open('db_info/user_types.csv') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row
            for row in csv_reader:
                user_type = row[0].strip()
                
                # Insert each user type
                insert_user_types(user_type)

def Read_notes() -> None:
    with open('db_info/notes.csv') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            note = row[0].strip()
            user_id = row[1].strip()
            created_by = row[2].strip()
            created_at = datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")  # Convert string to datetime
            last_updated_at = datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")  # Convert string to datetime
            
            # Insert each note
            insert_notes(note, user_id, created_by, created_at, last_updated_at)

def Read_user_machines() -> None:
    with open('db_info/user_machines.csv') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            equipment_id = int(row[0]).strip()  # Convert to integer
            completed_training = row[1].strip().lower() == 'true'
            user_id = row[2].strip()
            
            # Insert each user_machine
            insert_user_machines(equipment_id, completed_training, user_id)

def Read_equipment() -> None:
    with open('db_info/equipment.csv') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            equipment_name = row[0].strip()
            
            # Insert each equipment
            Insert_equipment(equipment_name)

def Read_event_log() -> None:
    with open('db_info/event_logs.csv') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            event_type_id = int(row[0]).strip()  # Convert to integer
            user_id = row[1].strip()
            timestamp = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")  # Convert string to datetime
            
            # Insert each event log
            Insert_event_log(event_type_id, user_id, timestamp)

def Read_event_types() -> None:
    with open('db_info/event_types.csv') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            event_type = row[0].strip()
            
            # Insert each event_type
            Insert_event_type(event_type)

def main() -> None:
    # Implement the creation
    metadata.create_all(engine)
    Read_user_types()
    Read_users()


if __name__ == "__main__":
    main()