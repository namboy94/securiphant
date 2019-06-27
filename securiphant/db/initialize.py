"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from securiphant.db import Base, uri
from securiphant.db.states.BooleanState import BooleanState
from securiphant.db.states.IntState import IntState


def initialize_database():
    """
    Initializes the database, creating all tables and filling default
    key-value pairs.
    :return: The database session
    """
    db_engine = create_engine(uri)
    Base.metadata.create_all(db_engine, checkfirst=True)
    _sessionmaker = sessionmaker(bind=db_engine)
    session = _sessionmaker()

    for state_type, key, default_value in [
        (BooleanState, "user_authorized", False),
        (BooleanState, "door_open", False),
        (BooleanState, "door_opened", False),
        (IntState, "temperature", -1),
        (IntState, "humidity", -1)
    ]:
        existing = session.query(state_type).filter_by(key=key).first()
        if existing is None:
            session.add(state_type(key=key, value=default_value))

    session.commit()
