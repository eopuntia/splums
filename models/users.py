from datetime import datetime

from sqlalchemy import Column, Integer, VARCHAR, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Relationship

from main import session

Model = declarative_base()
Model.query = session.query_property()

class users(Model):
    __tablename__ = 'users'

    bronco_id = Column(VARCHAR(255), primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    photo_url = Column(VARCHAR(255), nullable=False)
    user_type_id = Column(Integer(11), ForeignKey("user_types.user_type_id", ondelete="CASCADE"), nullable=False, index=True, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    last_updated_at = Column(DateTime, nullable=False, default=datetime.now())

    user = Relationship("user_types", back_populates="users")