"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

from securiphant.db import Base
from sqlalchemy import Column, Boolean, Integer
from datetime import datetime


class DoorOpenEvent(Base):
    """
    Event that gets stored whenever the door is opened
    """

    __tablename__ = "door_open_events"
    """
    The table's name
    """

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    """
    The ID of the event
    """

    timestamp = Column(Integer, nullable=False)
    """
    The time this event took place as a UNIX timestamp
    """

    duration = Column(Integer, nullable=False)
    """
    The duration that the door was open
    """

    was_authorized = Column(Boolean, nullable=False)
    """
    Whether or not the user was authorized while the door was opened
    """

    def __str__(self) -> str:
        """
        :return: The string representation of the event
        """
        date = datetime.fromtimestamp(self.timestamp)\
            .strftime("%Y-%m-%d:%H-%M-%S")
        return "{}: {}s, {}authorized".format(
            date,
            self.duration,
            "" if self.was_authorized else "not "
        )
