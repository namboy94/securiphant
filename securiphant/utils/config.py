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

import os
import json
import argparse
from typing import Dict, Any


config_dir = os.path.join(os.path.expanduser("~"), ".config/securiphant")
"""
The directory containing all config and data files for securiphant
"""


def load_config() -> Dict[str, Any]:
    """
    Loads the config for securiphant
    :return: The configuration data
    """
    config_file = os.path.join(config_dir, "config.json")
    with open(config_file, "r") as f:
        return json.load(f)


def write_config(data: Dict[str, Any]):
    """
    Writes data to the config file
    :param data: The data to write
    :return: None
    """
    config_file = os.path.join(config_dir, "config.json")
    with open(config_file, "w") as f:
        json.dump(data, f)
