"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""


import os
import sys
import json
from shutil import copyfile
from setuptools import setup, find_packages
from securiphant.db.initialize import initialize_database
from securiphant.config import load_config


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
            "PyQt5",
            "adafruit-blinka",
            "RPI.GPIO",
            "spidev",
            "mfrc522",
            "sqlalchemy"
        ],
        test_suite='nose.collector',
        tests_require=['nose'],
        include_package_data=True,
        zip_safe=False
    )

    if "install" in sys.argv:
        home = os.path.expanduser("~")
        systemd_dir = os.path.join(home, ".config/systemd/user")
        config_dir = os.path.join(home, ".config/securiphant")
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

        for key in ["openweathermap_api_key", "location_city"]:
            if key not in config_data:
                while True:
                    _input = input("Please enter a value for {}:".format(key))
                    if _input != "":
                        break
                config_data[key] = _input

        with open(config_file, "w") as f:
            json.dump(config_data, f)
