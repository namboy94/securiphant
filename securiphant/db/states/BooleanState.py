"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""


from securiphant.db import Base
from sqlalchemy import Column, String, Boolean


class BooleanState(Base):
    """
    SQLAlchemy table that stores boolean state values
    """

    __tablename__ = "bools"
    """
    The table's name
    """

    key = Column(String(255), primary_key=True, unique=True, nullable=False)
    """
    The key for the boolean value
    """

    value = Column(Boolean(), nullable=False)
    """
    The boolean value itself
    """

    def __str__(self) -> str:
        """
        :return: The string representation of the state
        """
        return str(self.value)
