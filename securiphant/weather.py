"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

import json
import requests
from typing import Dict
from securiphant.config import load_config


def get_weather(city: str) -> Dict[str, str]:
    """
    Gets the weather data for a specified city
    :param city: The city for which to get weather data
    :return: The weather data, including the following:
                - temperature
                - humidity
                - weather type
                - weather icon
    """
    api_key = load_config()["openweathermap_api_key"]
    url = "http://api.openweathermap.org/data/2.5/weather?" \
          "q={}&units=metric&APPID={}".format(city, api_key)

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
