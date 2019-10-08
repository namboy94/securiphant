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
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from securiphant.db.events.SpeakerEvent import SpeakerEvent


def queue_speaker_event(db_session: Session, text: str):
    """
    Queues a new speaker event in the database
    :param db_session: The database session to use
    :param text: The text to speak
    :return: None
    """
    event = SpeakerEvent(text=text, timestamp=int(time.time()))
    db_session.add(event)
    db_session.commit()


def speaker_loop():
    """
    Continuously checks for new speaker events and executes any ones that were
    not yet executed.
    :return: None
    """
    _sessionmaker = sessionmaker(bind=create_engine(generate_mysql_uri()))
    while True:
        session = _sessionmaker()

        events = session.query(SpeakerEvent).filter_by(executed=False).all()
        events.sort(key=lambda x: x.timestamp)
        for event in events:
            event.play()
            event.executed = True

        session.commit()
        time.sleep(0.1)
