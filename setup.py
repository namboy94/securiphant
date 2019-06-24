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
            "typing"
        ],
        test_suite='nose.collector',
        tests_require=['nose'],
        include_package_data=True,
        zip_safe=False
    )
