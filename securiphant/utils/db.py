"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.

securiphant is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

securiphant is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with securiphant.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from securiphant.db import Base, uri


# noinspection PyUnresolvedReferences
from securiphant.db.states.BooleanState import BooleanState
from securiphant.db.states.IntState import IntState


# noinspection PyUnresolvedReferences
def initialize_database():
    """
    Initializes the database, creating all tables and filling default
    key-value pairs.
    :return: The database session
    """
    from securiphant.db.states.BooleanState import BooleanState
    from securiphant.db.states.IntState import IntState
    from securiphant.db.events.DoorOpenEvent import DoorOpenEvent

    db_engine = create_engine(uri)
    Base.metadata.create_all(db_engine, checkfirst=True)
    _sessionmaker = sessionmaker(bind=db_engine)
    session = _sessionmaker()

    for state_type, key, default_value in [
        (BooleanState, "user_authorized", False),
        (BooleanState, "door_open", False),
        (BooleanState, "door_opened", False),
        (BooleanState, "going_out", False),
        (IntState, "temperature", -1),
        (IntState, "humidity", -1)
    ]:
        existing = session.query(state_type).filter_by(key=key).first()
        if existing is None:
            session.add(state_type(key=key, value=default_value))

    session.commit()


def get_int_state(key: str, session: Session) -> IntState:
    """
    Retrieves an int state from the database
    :param key: The key of the state entry
    :param session: The session to use for querying
    :return: The IntState object
    """
    return session.query(IntState).filter_by(key=key).first()


def get_boolean_state(key: str, session: Session) -> BooleanState:
    """
    Retrieves a boolean state from the database
    :param key: The key of the state entry
    :param session: The session to use for querying
    :return: The BooleanState object
    """
    return session.query(BooleanState).filter_by(key=key).first()
