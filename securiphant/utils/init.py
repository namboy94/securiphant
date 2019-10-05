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
from typing import List
from shutil import copyfile
from puffotter.os import makedirs
from puffotter.prompt import prompt, prompt_comma_list
from bokkichat.connection.impl.TelegramBotConnection import \
    TelegramBotConnection
from securiphant.utils.db import initialize_database, generate_mysql_uri
from securiphant.utils.config import config_dir, write_config
from securiphant.utils.systemd import reload_daemon, systemd_dir
from securiphant.utils.nfc import initialize_nfc_tag
from securiphant.alert_bot.AlertBot import AlertBot


def post_install():
    """
    Should be run after the installation in setup.py has finished
    :return: None
    """
    makedirs(systemd_dir)
    if not os.path.isdir(config_dir):
        makedirs(config_dir)
        write_config({})

    for service_file in os.listdir("systemd"):
        copyfile(
            os.path.join("systemd", service_file),
            os.path.join(systemd_dir, service_file)
        )
    reload_daemon()

    print("To finish configuring securiphant, run the following commands:")
    print("securiphant init <door|server|camera|display>")


def initialize(configurations: List[str]):
    """
    Initializes the securiphant installation
    :param configurations: The securiphant configurations run by this device
    :return: None
    """

    mysql_config = {
        "mysql_server": prompt("MySQL Server address: ", default="localhost"),
        "mysql_user": prompt("MySQL Username: "),
        "mysql_pass": prompt("MySQL Password: ")
    }
    uri = generate_mysql_uri(
        mysql_config["mysql_server"],
        mysql_config["mysql_user"],
        mysql_config["mysql_pass"]
    )
    initialize_database(uri)
    config = {"mysql": mysql_config}

    if "display" in configurations:
        config["openweathermap_api_key"] = \
            prompt("openweathermap.org API key: ")
        config["openweathermap_city"] = prompt("openweathermap city: ")
        print("Make sure that `PyQT5` is installed")

    if "door" in configurations:
        initialize_nfc_tag()

    if "server" in configurations:
        config["cameras"] = \
            prompt_comma_list("Connected Camera IDs: ", min_count=1)
        AlertBot.create_config(TelegramBotConnection, config_dir)
        print("Don't forget to connect a speaker!")
        print("Make sure that `opencv-python` and `flite` are installed")

    write_config(config)
