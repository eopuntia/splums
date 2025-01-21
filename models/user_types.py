from datetime import datetime

from sqlalchemy import Column, Integer, VARCHAR
from sqlalchemy.orm import declarative_base

from main import session

Model = declarative_base()
Model.query = session.query_property()


class user_types(Model):
    __tablename__ = 'user_types'

    user_type_id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
