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
import RPi.GPIO as GPIO
from threading import Lock
from securiphant.db import generate_mysql_uri
from securiphant.utils.db import get_boolean_state
from securiphant.db.events.DoorOpenEvent import DoorOpenEvent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


door_lock = Lock()
"""
Look for the door sensor to make sure two threads don't access the door
sensor at the same time
"""


# noinspection PyUnresolvedReferences
def is_open() -> bool:
    """
    Checks whether or not the door is open
    :return: True if the door is open, False otherwise
    """
    with door_lock:
        door_sensor_pin = 27
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(door_sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        return GPIO.input(door_sensor_pin) == 1


def door_check_loop():
    """
    Checks the door state and adjusts the database entries accordingly

    Two variables will be written to the database:

    is_open: Determines whether or not the door is currently open
    was_opened: Determines whether or not the door was opened in the past
    :return: None
    """
    _sessionmaker = sessionmaker(bind=create_engine(generate_mysql_uri()))

    open_start = None

    while True:

        session = _sessionmaker()

        door_open = get_boolean_state("door_open", session)
        door_opened = get_boolean_state("door_opened", session)

        if is_open():
            door_open.value = True
            door_opened.value = True

            if open_start is None:
                open_start = time.time()

        else:
            door_open.value = False

            if open_start is not None:
                was_authorized = \
                    get_boolean_state("user_authorized", session).value
                session.add(DoorOpenEvent(
                    timestamp=int(time.time()),
                    duration=int(time.time() - open_start),
                    was_authorized=was_authorized
                ))
                open_start = None

        session.commit()
        time.sleep(0.3)
