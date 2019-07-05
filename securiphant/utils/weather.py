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

import json
import requests
import argparse
from typing import Dict, Optional
from securiphant.utils.config import load_config, write_config


def get_weather() -> Optional[Dict[str, str]]:
    """
    Gets the weather data for a specified city
    :return: The weather data, including the following:
                - temperature
                - humidity
                - weather type
                - weather icon
    """
    config = load_config()
    api_key = config["openweathermap_api_key"]
    location = config["location_city"]
    url = "http://api.openweathermap.org/data/2.5/weather?" \
          "q={}&units=metric&APPID={}".format(location, api_key)

    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        return None
    response_data = json.loads(response.text)

    data = {
        "temperature": str(int((response_data["main"]["temp"]))),
        "humidity": str(int(response_data["main"]["humidity"])),
        "weather_type": response_data["weather"][0]["main"],
        "weather_icon":
            "http://openweathermap.org/img/wn/{}@2x.png"
            .format(response_data["weather"][0]["icon"])
    }
    return data


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

    print("Testing configuration: ")
    print(get_weather())
