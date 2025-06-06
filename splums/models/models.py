import datetime
from typing import List, Optional
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# The base class contains the registry of all ORM classes. Each specific ORM class inherits base
# to be added to the registry. Then, when you import Base in your other files you will have access
# to the ORM structure. You will also have to include the speicific ORM classes used. See the populate_database.py file.
class Base(DeclarativeBase):
    pass

class Department(Base):
    __tablename__ = 'department'

    department_id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(255))

    accounts: Mapped[List["Account"]] = relationship(back_populates="department")

class Affiliation(Base):
    __tablename__ = 'affiliation'

    affiliation_id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(255))
    icon_url: Mapped[str] = mapped_column(String(255))

    accounts: Mapped[List["Account"]] = relationship(back_populates="affiliation")

# Defines a table role in SQL, which corresponds to the Role class
class Role(Base):
    # sets the table name
    __tablename__ = 'role'

    # Mapped[int] means "use int python type", then, mapped_column is used for further specification. In this case, you say it is the primary key.
    role_id: Mapped[int] = mapped_column(primary_key=True)
    # same for this one, str is the python class, and String(255) corresponds to VARCHAR(255)
    name: Mapped[str] = mapped_column(String(255))

    # This indicates that many accounts can have one role. This is the array of accounts associated with each role.
    # These relationships are a big part of the ORM power. See the populate database, but it lets you query for all classes / add fields 
    # without needing to worry about the id specifically.
    # It is Mapped[List] as many accounts can correspond to each role.
    #The "Account" is saying that its grabbing the records from the Account table. The back_populates="role" is saying that THESE ROLES
    # will themselves populate the "role" field in account, so they both talk to each other. You will see a similar pattern in account
    accounts: Mapped[List["Account"]] = relationship(back_populates="role")

class Account(Base):
    __tablename__ = 'account'

    win: Mapped[int] = mapped_column(primary_key=True)
    # Similar to indicating the primary key with a mapped_column, information like ForeignKeys are implied by the mapped_column.
    # Together with the Mapped[int], Sql alchemy has all the needed information.
    role_id: Mapped[int] = mapped_column(ForeignKey("role.role_id"))
    affiliation_id: Mapped[int] = mapped_column(ForeignKey("affiliation.affiliation_id"))
    department_id: Mapped[int] = mapped_column(ForeignKey("department.department_id"))

    display_name: Mapped[str] = mapped_column(String(255))
    given_name: Mapped[str] = mapped_column(String(255))
    surname: Mapped[str] = mapped_column(String(255))
    photo_url: Mapped[str] = mapped_column(String(255))
    active_attendant: Mapped[bool] = mapped_column(default=False)
    swiped_in: Mapped[bool] = mapped_column(default=False)

    # Secure pin storage, default to NULL on user creation
    # Intend to check if NULL when a user logs in for the first time, and prompts them to set a new pin.
    # Pin can be either numbers, letters, or a combo, and will convert to string later when creating the pin in the db.
    pin_hash: Mapped[Optional[str]] = mapped_column(String(255))  

    rso: Mapped[Optional[str]] = mapped_column(String(255))

    private_note: Mapped[Optional[str]] = mapped_column(Text)
    public_note: Mapped[Optional[str]] = mapped_column(Text)

    # this syntax is slightly verbose and maybe there is a better way to do this, but it makes it so the timefield is automatically
    # populated to the current time whenever you add a record without needing to specify yourself.
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_updated_at: Mapped[datetime.datetime] = mapped_column( 
        DateTime(timezone=True), server_default=func.now()
    )
    last_access: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships where the account is the one in one-many
    # another field of foreign_keys is added for notes_subject and notes_creator since they both reference account ids so you need
    # to let SQL alchemy know which one is which.
    events: Mapped[List["Event"]] = relationship(back_populates="account", cascade="all, delete-orphan", foreign_keys="[Event.win]")
    equipments: Mapped[List["Account_Equipment"]] = relationship(back_populates="account", cascade="all, delete-orphan")
    
    # Relationships where the account is the many in one-many. 
    # This is the relationship that corresponds to the accounts field in Role.
    role: Mapped["Role"] = relationship(back_populates="accounts")
    affiliation: Mapped["Affiliation"] = relationship(back_populates="accounts")
    department: Mapped["Department"] = relationship(back_populates="accounts")

class Equipment(Base):
    __tablename__ = 'equipment'

    equipment_id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(255))
    icon_url: Mapped[str] = mapped_column(String(255))

    accounts: Mapped[List["Account_Equipment"]] = relationship(back_populates="equipment")

class Account_Equipment(Base):
    __tablename__ = 'account_equipment'

    account_equipment_id: Mapped[int] = mapped_column(primary_key=True)

    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.equipment_id"))
    win: Mapped[int] = mapped_column(ForeignKey("account.win"))

    equipment: Mapped["Equipment"] = relationship(back_populates="accounts")
    account: Mapped["Account"] = relationship(back_populates="equipments")

class Event_Type(Base):
    __tablename__ = 'event_type'

    event_type_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))

    events: Mapped[List["Event"]] = relationship(back_populates="event_type")

class Event(Base):
    __tablename__ = 'event'

    event_id: Mapped[int] = mapped_column(primary_key=True)
    event_type_id: Mapped[int] = mapped_column(ForeignKey("event_type.event_type_id"))
    win: Mapped[Optional[int]] = mapped_column(ForeignKey("account.win"))
    active_attendant: Mapped[Optional[int]] = mapped_column(ForeignKey("account.win"))
    occured_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    event_type: Mapped["Event_Type"] = relationship(back_populates="events")
    
    account: Mapped[Optional["Account"]] = relationship(back_populates="events", foreign_keys=[win])
 