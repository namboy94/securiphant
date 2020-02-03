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

import time
from securiphant.db import Base
from sqlalchemy import Column, String, Integer


class CheckIn(Base):
    """
    Class that defines a database table that tracks if services are
    running by making them check at set intervals.
    """

    __tablename__ = "check_ins"
    """
    The table's name
    """

    service = Column(
        String(255), primary_key=True, unique=True, nullable=False
    )
    """
    The name of the service
    """

    last_ping = Column(Integer(), nullable=False)
    """
    The last time the service checked in, as a unix timestamp
    """

    def is_alive(self) -> bool:
        """
        :return: Whether or not the service has checked in recently
        """
        return time.time() - self.last_ping < 10
