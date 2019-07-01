"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

import RPi.GPIO as GPIO


# noinspection PyUnresolvedReferences
def is_open() -> bool:
    """
    Checks whether or not the door is open
    :return: True if the door is open, False otherwise
    """
    door_sensor_pin = 27
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(door_sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    return GPIO.input(door_sensor_pin) == 1
