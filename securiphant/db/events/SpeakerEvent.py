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
from sqlalchemy import Column, String, Integer, Boolean
from subprocess import Popen, DEVNULL


class SpeakerEvent(Base):
    """
    Event that gets stored whenever a phrase is said on the speaker system
    """

    __tablename__ = "speaker_events"
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

    text = Column(String(255), nullable=False)
    """
    The text said over the speakers
    """

    executed = Column(Boolean, nullable=False, default=False)
    """
    Whether or not the speaker event was executed already
    """

    def play(self):
        """
        Plays the text over the speaker using flite
        :return: None
        """
        Popen(
            ["flite", "-voice", "awb", "-t", self.text],
            stdout=DEVNULL, stderr=DEVNULL
        ).wait()
