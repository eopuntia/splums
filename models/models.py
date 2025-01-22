from datetime import datetime
from sqlalchemy import Column, Integer, VARCHAR, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import declarative_base, Relationship
from main import session

Model = declarative_base()
Model.query = session.query_property()


class event_logs(Model):
    __tablename__ = 'event_logs'

    event_id = Column(Integer, primary_key=True, autoincrement=True)
    event_type_id = Column(Integer, ForeignKey("event_types.event_types_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(VARCHAR(255), ForeignKey("users.bronco_id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)

    event_type = Relationship("event_types", back_populates="events")
    user = Relationship("users", back_populates="user_logs")


class event_types(Model):
    __tablename__ = 'event_types'

    event_types_id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(VARCHAR(255), nullable=False)

    events = Relationship("event_logs", back_populates="event_type")

class notes(Model):
    __tablename__ = 'notes'

    notes_id = Column(Integer, primary_key=True, autoincrement=True)
    note = Column(VARCHAR(255), nullable=False)
    user_id = Column(VARCHAR(255), ForeignKey("users.bronco_id", ondelete="CASCADE"), nullable=False, index=True)
    created_by = Column(VARCHAR(255), ForeignKey("users.bronco_id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    last_updated_at = Column(DateTime, nullable=False, default=datetime.now)

    user = Relationship("users", back_populates="notes")

class user_types(Model):
    __tablename__ = 'user_types'

    user_type_id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255), nullable=False)

    users = Relationship("users", back_populates="user_type")

class users(Model):
    __tablename__ = 'users'

    bronco_id = Column(VARCHAR(255), primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    photo_url = Column(VARCHAR(255), nullable=False)
    user_type_id = Column(Integer, ForeignKey("user_types.user_type_id", ondelete="CASCADE"), nullable=False, index=True, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    last_updated_at = Column(DateTime, nullable=False, default=datetime.now)

    user_type = Relationship("user_types", back_populates="users")
    notes = Relationship("notes", back_populates="user")
    user_logs = Relationship("event_logs", back_populates="user")
    user_machines = Relationship("user_machines", back_populates="user")

class equipment(Model):
    __tablename__ = 'equipment'

    equipment_id = Column(Integer, primary_key=True)
    equipment_name = Column(VARCHAR(255), nullable=False)

    machines = Relationship("user_machines", back_populates="machine")

class user_machines(Model):
    __tablename__ = 'user_machines'

    user_machine_id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, ForeignKey("equipment.equipment_id", ondelete="CASCADE"), nullable=False, index=True)
    completed_training = Column(Boolean, nullable=False, default=False)
    user_id = Column(VARCHAR(255), ForeignKey("users.bronco_id", ondelete="CASCADE"), nullable=False, index=True)
    machine = Relationship("equipment", back_populates="machines")
    user = Relationship("users", back_populates="user_machines")
