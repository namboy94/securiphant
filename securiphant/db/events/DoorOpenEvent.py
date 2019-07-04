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
