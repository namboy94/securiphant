"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

import os
import json
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
