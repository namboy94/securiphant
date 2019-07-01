"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

import RPi.GPIO as GPIO
from pirc522 import RFID
from mfrc522 import SimpleMFRC522


def write_nfc_data(data: str):
    """
    Writes a string to an NFC tag
    :param data: The data to write
    :return: None
    """
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
