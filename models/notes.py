from datetime import datetime

from sqlalchemy import Column, Integer, VARCHAR, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Relationship

from main import session

Model = declarative_base()
Model.query = session.query_property()

class notes(Model):
    __tablename__ = 'notes'

    notes_id = Column(int(255), primary_key=True, autoincrement=True)
    note = Column(VARCHAR(255), nullable=False)
    user_id = Column(VARCHAR(255), ForeignKey("users.bronco_id", ondelete="CASCADE"), nullable=False, index=True, unique=True)
    created_by = Column(VARCHAR(255), ForeignKey("users.bronco_id", ondelete="CASCADE"), nullable=False, index=True, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    last_updated_at = Column(DateTime, nullable=False, default=datetime.now())

    user = Relationship("users", back_populates="notes")