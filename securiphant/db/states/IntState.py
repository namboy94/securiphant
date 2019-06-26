"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""


from securiphant.db import Base
from sqlalchemy import Column, String, Integer


class IntState(Base):
    """
    SQLAlchemy table that stores integer state values
    """

    __tablename__ = "ints"
    """
    The table's name
    """

    key = Column(String(255), primary_key=True, unique=True, nullable=False)
    """
    The key for the integer value
    """

    value = Column(Integer(), nullable=False)
    """
    The int value itself
    """
