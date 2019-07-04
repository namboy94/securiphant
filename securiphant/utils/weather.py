"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

import json
import requests
import argparse
from typing import Dict
from securiphant.utils.config import load_config, write_config


def get_weather() -> Dict[str, str]:
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

    response = requests.get(url)
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
