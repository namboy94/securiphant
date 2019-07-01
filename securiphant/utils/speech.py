"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

from subprocess import call, PIPE


def speak(text: str):
    """
    Uses the speakers to say a phrase
    :param text: The text to speak
    :return: None
    """
    call(["espeak", text], stderr=PIPE, stdout=PIPE)
