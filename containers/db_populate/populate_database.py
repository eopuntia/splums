import csv # For reading DB information

import logging # For debug information
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import Column, Integer, VARCHAR, ForeignKey, DateTime, Boolean, Insert

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
    Column("win", VARCHAR(255), primary_key=True, unique=True),
    Column("name", VARCHAR(255), nullable=False),
    Column("photo_url", VARCHAR(255), nullable=False),
    Column("user_type_id", Integer, ForeignKey("user_types.user_type_id", ondelete="CASCADE"), nullable=False, index=True, unique=True),
    Column("created_at", DateTime, nullable=False, default=datetime.now),
    Column("last_updated_at", DateTime, nullable=False, default=datetime.now),
    Column("swiped_in", Boolean, nullable=False),
    Column("last_access", DateTime, nullable=False, default=datetime.now)
)

# Create user_types table
user_types_table = sa.Table(
    "user_types", 
    metadata,
    Column("user_type_id", Integer, primary_key=True, unique=True, autoincrement=True),
    Column("user_type", VARCHAR(255), nullable=False, unique=True)
)

# Create notes table
notes_table = sa.Table(
    "notes",
    metadata,
    Column("note_id", Integer, primary_key=True, autoincrement=True),
    Column("note", VARCHAR(255), nullable=False),
    Column("user_id", VARCHAR(255), ForeignKey("users.win", ondelete="CASCADE"), nullable=False, index=True),
    Column("created_by", VARCHAR(255), ForeignKey("users.win", ondelete="CASCADE"), nullable=False, index=True),
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
    Column("user_id", VARCHAR(255), ForeignKey("users.win", ondelete="CASCADE"), nullable=False, index=True),
)

# Create equipment table
equipment_table = sa.Table(
    "equipment",
    metadata,
    Column("equipment_id", Integer, primary_key=True, autoincrement=True),
    Column("equipment_name", VARCHAR(255), nullable=False, unique=True)
)

# Create event_logs table
event_logs_table = sa.Table(
    "event_logs",
    metadata,
    Column("event_id", Integer, primary_key=True, autoincrement=True),
    Column("event_type_id", Integer, ForeignKey("event_types.event_types_id", ondelete="CASCADE"), nullable=False, index=True),
    Column("user_id", VARCHAR(255), ForeignKey("users.win", ondelete="CASCADE"), nullable=False, index=True),
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
def Insert_user(win: str, name: str, photo_url: str, user_type_id: int, created_at: datetime, last_updated_at: datetime, swiped_in: bool, last_access: datetime) -> None:
    with engine.connect() as conn:
        query_check = sa.select(users_table).where((users_table.c.win == win))
        result = conn.execute(query_check).fetchone()
        conn.commit()

        if not result:
            query_insert = Insert(users_table).values(
                win=win, 
                name=name, 
                photo_url=photo_url, 
                user_type_id=user_type_id, 
                created_at=created_at, 
                last_updated_at=last_updated_at,
                swiped_in=swiped_in,
                last_access=last_access
            )
            conn.execute(query_insert)
            conn.commit()
            print(f"Inserted user: {win}")
        else:
            print(f"User '{win}' already exists.")

# Inserts user types into user_types table
def Insert_user_types(user_type: str) -> None:
    with engine.connect() as conn:
        query_check = sa.select(user_types_table).where(user_types_table.c.user_type == user_type)
        result = conn.execute(query_check).fetchone()
        conn.commit()
        
        if not result:  # Insert only if the user_type doesn't exist
            query_insert = Insert(user_types_table).values(user_type=user_type)
            conn.execute(query_insert)
            conn.commit()
            print(f"Inserted user type: {user_type}")
        else:
            print(f"User type '{user_type}' already exists.")


# Inserts notes into notes table
def Insert_notes(note: str, user_id: str, created_by: str, created_at: datetime, last_updated_at: datetime) -> None:
    with engine.connect() as conn:
        query_check = sa.select(notes_table).where(
            (notes_table.c.note == note) &
            (notes_table.c.user_id == user_id) &
            (notes_table.c.created_by == created_by) &
            (notes_table.c.created_at == created_at) &
            (notes_table.c.last_updated_at == last_updated_at)
            )
        result = conn.execute(query_check).fetchone()
        conn.commit()
        
        if not result:  # Insert only if the user_type doesn't exist
            query_insert = Insert(notes_table).values(
            note=note,
            user_id=user_id,
            created_by=created_by,
            created_at=created_at,
            last_updated_at=last_updated_at
            )
            conn.execute(query_insert)
            conn.commit()
            print(f"Inserted note for: {user_id}")
        else:
            print(f"Note for'{user_id}' already exists.")

# Inserts user machines into user_machines table
def Insert_user_machines(equipment_id: int, completed_training: bool, user_id: str) -> None:
    with engine.connect() as conn:
        query_check = sa.select(user_machines_table).where(
            (user_machines_table.c.equipment_id == equipment_id) &
            (user_machines_table.c.completed_training == completed_training) &
            (user_machines_table.c.user_id == user_id)
            )
        result = conn.execute(query_check).fetchone()
        conn.commit()
        
        if not result:  # Insert only if the user_type doesn't exist
            query_insert = Insert(user_machines_table).values(
            equipment_id=equipment_id,
            completed_training=completed_training,
            user_id=user_id
            )
            conn.execute(query_insert)
            conn.commit()
            print(f"Inserted user machine for: {user_id}")
        else:
            print(f"User machine for'{user_id}' already exists.")

# Inserts equipment into equipment table
def Insert_equipment(equipment_name: str) -> None:
    with engine.connect() as conn:
        query_check = sa.select(equipment_table).where(equipment_table.c.equipment_name == equipment_name)
        result = conn.execute(query_check).fetchone()
        conn.commit()
        
        if not result:  # Insert only if the user_type doesn't exist
            query_insert = Insert(equipment_table).values(equipment_name=equipment_name)
            conn.execute(query_insert)
            conn.commit()
            print(f"Inserted equipment type: {equipment_name}")
        else:
            print(f"Equipment type '{equipment_name}' already exists.")

# Inserts new event log into event_log table
def Insert_event_log(event_type_id: int, user_id: str, timestamp: datetime) -> None:
    with engine.connect() as conn:
        query_check = sa.select(event_logs_table).where(
            (event_logs_table.c.event_type_id == event_type_id) and
            (event_logs_table.c.user_id == user_id) and
            (event_logs_table.c.timestamp == timestamp)
            )
        result = conn.execute(query_check).fetchone()
        conn.commit()
        
        if not result:  # Insert only if the user_type doesn't exist
            query_insert =  query = Insert(event_logs_table).values(
            event_type_id=event_type_id,
            user_id=user_id,
            timestamp=timestamp
            )
            conn.execute(query_insert)
            conn.commit()
            print(f"Inserted event log: {user_id}")
        else:
            print(f"Event log for '{user_id}' already exists.")
       
# Inserts event type into event_type table
def Insert_event_type(event_type: str) -> None:
    with engine.connect() as conn:
        query_check = sa.select(event_types_table).where(event_types_table.c.event_type == event_type)
        result = conn.execute(query_check).fetchone()
        conn.commit()
        
        if not result:  # Insert only if the user_type doesn't exist
            query_insert = Insert(event_types_table).values(event_type=event_type)
            conn.execute(query_insert)
            conn.commit()
            print(f"Inserted event type: {event_type}")
        else:
            print(f"Event type '{event_type}' already exists.")

#*******************************************************************************************
# READ DB INFO
#*******************************************************************************************


def Read_users() -> None:
    with open('db_info/users.csv') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        reset_auto_increment("users")
        for row in csv_reader:
            win = row[0].strip()  # Strip any extra whitespace
            name = row[1].strip()
            photo_url = row[2].strip()
            user_type_id = int(row[3].strip())  # Convert user_type_id to integer and strip extra spaces
            created_at = datetime.strptime(row[4].strip(), "%Y-%m-%d %H:%M:%S")  # Convert to datetime and strip spaces
            last_updated_at = datetime.strptime(row[5].strip(), "%Y-%m-%d %H:%M:%S")
            swiped_in = row[6].strip().lower() == 'true'
            last_access = row[7].strip()

            # Insert each user
            Insert_user(win, name, photo_url, user_type_id, created_at, last_updated_at, swiped_in, last_access)


def Read_user_types() -> None:
    with open('db_info/user_types.csv') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row
            reset_auto_increment("user_types")
            for row in csv_reader:
                user_type = row[0].strip()
                
                # Insert each user type
                Insert_user_types(user_type)

def Read_notes() -> None:
    with open('db_info/notes.csv') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        reset_auto_increment("notes")
        for row in csv_reader:
            note = row[0].strip()
            user_id = row[1].strip()
            created_by = row[2].strip()
            created_at = datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")  # Convert string to datetime
            last_updated_at = datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")  # Convert string to datetime
            
            # Insert each note
            Insert_notes(note, user_id, created_by, created_at, last_updated_at)

def Read_user_machines() -> None:
    with open('db_info/user_machines.csv') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        reset_auto_increment("user_machines")
        for row in csv_reader:
            equipment_id = int(row[0].strip())  # Convert to integer
            completed_training = row[1].strip().lower() == 'true'
            user_id = row[2].strip()
            
            # Insert each user_machine
            Insert_user_machines(equipment_id, completed_training, user_id)

def Read_equipment() -> None:
    with open('db_info/equipment.csv') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        reset_auto_increment("equipment")
        for row in csv_reader:
            equipment_name = row[0].strip()
            
            # Insert each equipment
            Insert_equipment(equipment_name)

def Read_event_log() -> None:
    with open('db_info/event_logs.csv') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        reset_auto_increment("event_logs")
        for row in csv_reader:
            event_type_id = int(row[0].strip())  # Convert to integer
            user_id = row[1].strip()
            timestamp = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")  # Convert string to datetime
            
            # Insert each event log
            Insert_event_log(event_type_id, user_id, timestamp)

def Read_event_types() -> None:
    with open('db_info/event_types.csv') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        reset_auto_increment("event_types")
        for row in csv_reader:
            event_type = row[0].strip()
            
            # Insert each event_type
            Insert_event_type(event_type)

# Reset auto increment to 1 for each given table to prevent insertion from saved PK index
def reset_auto_increment(table_name: str) -> None:
    with engine.connect() as conn:
        query = sa.text(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1;")
        conn.execute(query)

def main() -> None:
    # Implement the creation
    metadata.create_all(engine)

    # Start reading and inserting data
    Read_user_types()
    Read_users()
    Read_notes()
    Read_equipment()
    Read_user_machines()
    Read_event_types()
    Read_event_log()


if __name__ == "__main__":
    main()
