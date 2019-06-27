"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

from mfrc522 import SimpleMFRC522


def write_nfc_data(data: str):
    """
    Writes a string to an NFC tag
    :param data: The data to write
    :return: None
    """
    writer = SimpleMFRC522()
    writer.write(data)


def read_nfc_data() -> str:
    """
    Reads an NFC tag's content
    :return: The data on the NFC tag
    """
    reader = SimpleMFRC522()
    _, text = reader.read()
    return text
