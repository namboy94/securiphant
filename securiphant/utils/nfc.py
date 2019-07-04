"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

import time
import RPi.GPIO as GPIO
from pirc522 import RFID
from mfrc522 import SimpleMFRC522
from threading import Lock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from securiphant.utils.crypto import verify_password, generate_random,\
    generate_hash
from securiphant.utils.config import load_config, write_config
from securiphant.db import uri
from securiphant.utils.db import get_boolean_state
from securiphant.utils.speech import speak


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
    engine = create_engine(uri)
    _sessionmaker = sessionmaker(bind=engine)

    while True:

        key = read_nfc_data()
        _hash = load_config()["nfc_hash"]

        if verify_password(key, _hash):
            session = _sessionmaker()
            user_authorized = get_boolean_state("user_authorized", session)

            user_authorized.value = not user_authorized.value
            session.commit()

            if user_authorized.value:
                speak("Welcome Home!")
            else:
                going_out = get_boolean_state("going_out", session)
                door_opened = get_boolean_state("door_opened", session)

                going_out.value = True
                session.commit()
                speak("Goodbye.")
                time.sleep(10)  # Give user time to leave

                going_out.value = False
                door_opened.value = False
                session.commit()

        time.sleep(3)


def initialize_nfc_tag():
    """
    Writes a key to an NFC tag and stores the hash in the configuration
    :return: None
    """
    config = load_config()

    key = generate_random(48)  # Maximum capacity of NFC tag
    _hash = generate_hash(key)

    speak("Hold the NFC tag to the sensor now")
    write_nfc_data(key)
    speak("NFC Tag written successfully")

    config["nfc_hash"] = _hash
    write_config(config)
