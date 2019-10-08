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
from typing import List, Dict, Any
from puffotter.prompt import prompt, prompt_comma_list
from bokkichat.connection.impl.TelegramBotConnection import \
    TelegramBotConnection
from urllib.request import urlretrieve
from securiphant.utils.db import initialize_database
from securiphant.utils.config import config_dir, write_config, load_config


def initialize(configurations: List[str]):
    """
    Initializes the securiphant installation
    :param configurations: The securiphant configurations run by this device
    :return: None
    """

    config = {"mysql": {
        "server": prompt("MySQL Server address: ", default="localhost"),
        "user": prompt("MySQL Username: "),
        "pass": prompt("MySQL Password: ")
    }}  # type: Dict[str, Any]
    write_config(config)
    initialize_database()

    if "server" in configurations or "display" in configurations:
        config["openweathermap_api_key"] = \
            prompt("openweathermap.org API key: ")
        config["openweathermap_city"] = prompt("openweathermap city: ")

    if "display" in configurations:
        print("Make sure that `PyQT5` is installed")

    if "door" in configurations:
        from securiphant.utils.nfc import initialize_nfc_tag
        config["nfc_hash"] = initialize_nfc_tag()

    if "server" in configurations:
        voice_file = os.path.join(config_dir, "voice.flitevox")
        if os.path.isfile(voice_file):
            print("Downloading flite voice file...")
            urlretrieve("http://www.festvox.org/flite/packed/flite-2.0/"
                        "voices/cmu_us_aew.flitevox", voice_file)

        from securiphant.alert_bot.AlertBot import AlertBot
        config["cameras"] = prompt_comma_list(
            "Connected Camera IDs: ", min_count=1, primitive_type=int
        )
        print("Alert Bot Configuration:")
        AlertBot.create_config(TelegramBotConnection, config_dir)
        config.update(load_config())  # Need to get values stored by bot
        print("Don't forget to connect a speaker!")
        print("Make sure that `opencv-python` and `flite` are installed")

    write_config(config)
