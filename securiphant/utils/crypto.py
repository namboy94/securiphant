"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

import bcrypt
import random
import string
# TODO Put this in a library, this shouldn't be a part of this project


def generate_random(length: int) -> str:
    """
    Generates a random byte string consisting of alphanumeric characters
    Thanks @ Albert (https://stackoverflow.com/users/281021/albert)
    https://stackoverflow.com/questions/2257441
    :param length: The length of the string to generate
    :return: The generated random byte string
    """
    return bytes(
        "".join(random.choice(string.ascii_uppercase + string.digits)
                for _ in range(length)),
        "utf-8"
    ).decode("utf-8")


def generate_hash(password: str) -> str:
    """
    Salts and hashes a password to generate a hash for storage in a database
    :param password: The password to hash
    :return: The hash of the password
    """
    password = bytes(password, "utf-8")
    return bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str):
    """
    Verifies that a password matches a given hash
    :param password: The password to verify
    :param hashed: The hash to verify the password against
    :return: True if the password matches, otherwise False
    """
    password = bytes(password, "utf-8")
    hashed = bytes(hashed, "utf-8")

    try:
        return bcrypt.checkpw(password, hashed)
    except ValueError:
        return False
