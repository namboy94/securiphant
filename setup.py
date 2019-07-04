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
    from securiphant.utils.db import initialize_database
    from securiphant.utils.config import config_dir, write_config
    from securiphant.utils.systemd import reload_daemon

    systemd_dir = \
        os.path.join(os.path.expanduser("~"), ".config/systemd/user")

    if not os.path.isdir(systemd_dir):
        os.makedirs(systemd_dir)
    if not os.path.isdir(config_dir):
        os.makedirs(config_dir)
        write_config({})

    initialize_database()

    for service_file in os.listdir("systemd"):
        copyfile(
            os.path.join("systemd", service_file),
            os.path.join(systemd_dir, service_file)
        )
    reload_daemon()

    print("Make sure that `opencv-python` and `PyQT5` are installed")
    print("Please make sure that the following other programs are installed:")
    print("systemd\nraspistill\nraspivid\nMP4Box\nespeak")
    print("To finish configuring securiphant, run the following commands:")
    print("securiphant-nfc-initialize")
    print("securiphant-weather-initialize <API_KEY> <LOCATION>")
    print("securiphant-alert-bot --initialize")


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
            "RPI.GPIO",
            "spidev",
            "mfrc522",
            "pi-rc522",
            "sqlalchemy",
            "kudubot",
            "bokkichat",
            "bcrypt",
            "Adafruit_DHT",
            # "opencv-python",
            # "PyQt5"
        ],
        test_suite='nose.collector',
        tests_require=['nose'],
        include_package_data=True,
        zip_safe=False
    )

    if "install" in sys.argv:
        post_install()
