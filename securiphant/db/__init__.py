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

from sqlalchemy.ext.declarative import declarative_base
from securiphant.utils.config import load_config


Base = declarative_base()
"""
The base database table class
"""


def generate_mysql_uri() -> str:
    """
    Generates a mysql URI for the stored confiuration
    :return: The generated URI
    """
    config = load_config()["mysql"]
    return "mysql://{}:{}@{}/securiphant".format(
        config["user"], config["pass"], config["server"]
    )
