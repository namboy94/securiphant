"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

# noinspection PyUnresolvedReferences
import Adafruit_DHT
import time
from threading import Lock
from typing import Tuple, Optional
from securiphant.db import uri
from securiphant.utils.db import get_int_state
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


environment_lock = Lock()
"""
Lock that makes sure no two threads ever access the environment sensor at the
same time.
"""


def get_environment_data() -> Tuple[Optional[int], Optional[int]]:
    """
    Reads the temperature and humidity from an Adafruit DHT22 sensor
    :return: The temperature, the humidity in integer values
    """
    with environment_lock:
        sensor = Adafruit_DHT.DHT22
        pin = 18

        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

        try:
            return int(temperature), int(humidity)
        except TypeError:
            return None, None


def environment_check_loop():
    """
    Checks the DFT22 sensor for temperature and humidity values
    and stores the result in the database
    :return: None
    """
    engine = create_engine(uri)
    _sessionmaker = sessionmaker(bind=engine)

    while True:
        session = _sessionmaker()
        temperature, humidity = get_environment_data()
        db_temperature = get_int_state("temperature", session)
        db_humidity = get_int_state("humidity", session)

        if temperature is not None:
            db_temperature.value = temperature
        if humidity is not None:
            db_humidity.value = humidity

        session.commit()
        time.sleep(2)  # New data arrives every 2 seconds with this sensor
