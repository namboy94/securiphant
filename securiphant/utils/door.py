"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

import time
import RPi.GPIO as GPIO
from threading import Lock
from securiphant.db import uri
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
    _sessionmaker = sessionmaker(bind=create_engine(uri))

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
