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
import logging
import RPi.GPIO as GPIO
from pirc522 import RFID
from mfrc522 import SimpleMFRC522
from threading import Lock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from puffotter.crypto import verify_password, generate_random, generate_hash
from securiphant.utils.config import load_config
from securiphant.db import generate_mysql_uri
from securiphant.utils.db import get_boolean_state
from securiphant.utils.speech import queue_speaker_event


nfc_lock = Lock()
"""
Lock that ensures that two threads don't access the NFC sensor at the same time
"""


def write_nfc_data(data: str):
    """
    Writes a string to an NFC tag
    :param data: The data to write
    :return: None
    """
    with nfc_lock:
        try:
            writer = SimpleMFRC522()
            writer.write(data)
        finally:
            # noinspection PyUnresolvedReferences
            GPIO.cleanup()


def read_nfc_data() -> str:
    """
    Reads an NFC tag's content
    :return: The data on the NFC tag
    """
    with nfc_lock:
        # We need to use the pirc522 library's waiting functionality here to
        # avoid using 100% CPU (which is the case for mfrc522)
        reader = RFID()
        reader.wait_for_tag()
        reader.cleanup()

        # And here we use mfrc522 to actually read the data
        try:
            reader = SimpleMFRC522()
            _, text = reader.read()
            return text
        finally:
            # noinspection PyUnresolvedReferences
            GPIO.cleanup()


def nfc_check_loop():
    """
    Checks whether the NFC reader reads an authenticated NFC tag

    If a authenticated tag is held against the sensor, the value
    `is_authenticated` is set to True in the shared database.

    Authentication also resets the `door_opened` value to False.

    Checking out sets the `going_out` value to True for 10 seconds, after which
    the system will be re-armed
    :return:
    """
    engine = create_engine(generate_mysql_uri())
    _sessionmaker = sessionmaker(bind=engine)
    logger = logging.getLogger("nfc-sensor")

    while True:

        logger.info("Waiting for NFC Tag...")
        key = read_nfc_data()
        logger.info("NFC Tag detected")

        _hash = load_config()["nfc_hash"]

        if verify_password(key, _hash):
            logger.info("Authentication successful")
            session = _sessionmaker()
            user_authorized = get_boolean_state("user_authorized", session)

            user_authorized.value = not user_authorized.value
            session.commit()

            if user_authorized.value:
                logger.debug("User returned home")
                queue_speaker_event(session, "Welcome Home!")
            else:
                logger.debug("User leaving")
                going_out = get_boolean_state("going_out", session)
                door_opened = get_boolean_state("door_opened", session)

                going_out.value = True
                session.commit()
                queue_speaker_event(session, "Goodbye.")
                time.sleep(10)  # Give user time to leave

                going_out.value = False
                door_opened.value = False
                session.commit()
        else:
            logger.info("Authentication unsuccessful")

        time.sleep(3)


def initialize_nfc_tag() -> str:
    """
    Writes a key to an NFC tag and returns the hash
    :return: None
    """
    key = generate_random(48)  # Maximum capacity of NFC tag
    _hash = generate_hash(key)

    print("Hold the NFC tag to the sensor now")
    write_nfc_data(key)
    print("NFC Tag written successfully")

    return _hash
