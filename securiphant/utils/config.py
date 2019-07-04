"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
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


def initialize_weather_config():
    """
    Initializes the weather configuration using CLI arguments
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("openweathermap_api_key",
                        help="The API Key for openweathermap.org")
    parser.add_argument("location_city",
                        help="The city for which to display weather data")
    args = parser.parse_args()
    config = load_config()
    config["openweathermap_api_key"] = args.openweathermap_api_key
    config["location_city"] = args.location_city
    write_config(config)
