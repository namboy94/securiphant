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
