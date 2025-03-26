import os
import sqlalchemy as sa
#import gui
import sys

from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import scoped_session, sessionmaker
from PyQt6.QtWidgets import QApplication


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

engine = sa.create_engine("mariadb+mariadbconnector://splums:example@127.0.0.1:3307/splums")

session = scoped_session(
    sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine
    )
)

def get_session():
    return session
