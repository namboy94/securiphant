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

    def __str__(self) -> str:
        """
        :return: The string representation of the state
        """
        return str(self.value)
