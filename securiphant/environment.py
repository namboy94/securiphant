"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

# noinspection PyUnresolvedReferences
import Adafruit_DHT
from typing import Tuple, Optional


def get_environment_data() -> Tuple[Optional[int], Optional[int]]:
    """
    Reads the temperature and humidity from an Adafruit DHT22 sensor
    :return: The temperature, the humidity in integer values
    """

    sensor = Adafruit_DHT.DHT22
    pin = 18

    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

    try:
        return int(temperature), int(humidity)
    except TypeError:
        return None, None
