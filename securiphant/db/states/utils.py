"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

from sqlalchemy.orm import Session
from securiphant.db.states.BooleanState import BooleanState
from securiphant.db.states.IntState import IntState


def get_boolean_state(key: str, session: Session) -> BooleanState:
    """
    Retrieves a boolean state from the database
    :param key: The key of the state entry
    :param session: The session to use for querying
    :return: The BooleanState object
    """
    return session.query(BooleanState).filter_by(key=key).first()


def get_int_state(key: str, session: Session) -> IntState:
    """
    Retrieves an int state from the database
    :param key: The key of the state entry
    :param session: The session to use for querying
    :return: The IntState object
    """
    return session.query(IntState).filter_by(key=key).first()
