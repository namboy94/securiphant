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
import sys
from shutil import copyfile
from setuptools import setup, find_packages

setup(
    name="securiphant",
    version=open("version", "r").read(),
    description="A surveillance, security and home automation solution",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    author="Hermann Krumrey",
    author_email="hermann@krumreyh.com",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
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
        "puffotter",
        "phue"
    ],
    extras_require={
        "display": ["PyQt5"],
        "camera": ["opencv-python"]
    },
    test_suite="nose.collector",
    tests_require=["nose"],
    include_package_data=True,
    zip_safe=False
)

if "install" in sys.argv:
    from securiphant.utils.config import config_dir, write_config
    from securiphant.utils.systemd import systemd_dir, reload_daemon

    if not os.path.isdir(systemd_dir):
        os.makedirs(systemd_dir)
    if not os.path.isdir(config_dir):
        os.makedirs(config_dir)
        write_config({})

    for service_file in os.listdir("systemd"):
        copyfile(
            os.path.join("systemd", service_file),
            os.path.join(systemd_dir, service_file)
        )
    reload_daemon()

    print("To finish configuring securiphant, run the following commands:")
    print("securiphant init <door|server|camera|display>")
