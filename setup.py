"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""


import os
from setuptools import setup, find_packages

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
            "PyQt5",
            "adafruit-blinka",
            "RPI.GPIO",
            "spidev",
            "mfrc522"
        ],
        test_suite='nose.collector',
        tests_require=['nose'],
        include_package_data=True,
        zip_safe=False
    )
