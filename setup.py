"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""


import os
import sys
from shutil import copyfile
from setuptools import setup, find_packages


def post_install():
    """
    Post Installation Script
    :return: None
    """
    from securiphant.db.initialize import initialize_database
    from securiphant.config import load_config, config_dir, write_config
    from securiphant.alert_bot.AlertBot import AlertBot

    systemd_dir = \
        os.path.join(os.path.expanduser("~"), ".config/systemd/user")
    config_file = os.path.join(config_dir, "config.json")

    if not os.path.isdir(systemd_dir):
        os.makedirs(systemd_dir)
    if not os.path.isdir(config_dir):
        os.makedirs(config_dir)

    for service_file in os.listdir("systemd"):
        copyfile(
            os.path.join("systemd", service_file),
            os.path.join(systemd_dir, service_file)
        )

    initialize_database()

    if os.path.isfile(config_file):
        config_data = load_config()
    else:
        config_data = {}

    print("Enter config data:")
    for key in [
        "openweathermap_api_key",
        "location_city",
        "telegram_address"
    ]:
        if key not in config_data:
            while True:
                _input = input("Please enter a value for {}:".format(key))
                if _input != "":
                    break
            config_data[key] = _input

    write_config(config_data)

    from bokkichat.connection.impl.TelegramBotConnection import \
        TelegramBotConnection
    from kudubot.exceptions import ConfigurationError

    try:
        bot = AlertBot.load(TelegramBotConnection, config_dir)
    except ConfigurationError as e:
        print("Set Up Alert Bot:")
        AlertBot.create_config(TelegramBotConnection, config_dir)

    print("If you have not done so already, "
          "run 'securiphant-initialize-nfc' to initialize the NFC tag")


if __name__ == "__main__":

    setup(
        name="securiphant",
        version=open("version", "r").read(),
        description="A surveillance, security and home automation solution",
        long_description=open("README.md", "r").read(),
        long_description_content_type="text/markdown",
        author="Hermann Krumrey",
        author_email="hermann@krumreyh.com",
        classifiers=[
            "License :: Other/Proprietary License"
        ],
        url="https://gitlab.namibsun.net/namibsun/python/securiphant",
        license="GNU GPL3",
        packages=find_packages(),
        scripts=list(map(lambda x: os.path.join("bin", x), os.listdir("bin"))),
        install_requires=[
            "typing",
            "requests",
            "adafruit-blinka",
            "RPI.GPIO",
            "spidev",
            "mfrc522",
            "sqlalchemy",
            "kudubot",
            "bokkichat",
            "bcrypt",
            "Adafruit_DHT",
            # "PyQt5"
        ],
        test_suite='nose.collector',
        tests_require=['nose'],
        include_package_data=True,
        zip_safe=False
    )

    if "install" in sys.argv:
        post_install()
