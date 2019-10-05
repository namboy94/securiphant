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
from subprocess import call, PIPE


securiphant_services = {
    "door": [
        "securiphant-door-sensor",
        "securiphant-nfc-sensor",
        # "securiphant-environment-sensor"
    ],
    "display": [
        "securiphant-display"
    ],
    "server": [
        "securiphant-alert-bot",
        # "securiphant-environment-sensor"
    ]
}
"""
A dictionary mapping securiphant configurations to systemd services
"""

systemd_dir = os.path.join(os.path.expanduser("~"), ".config/systemd/user")
"""
Thje directory containing systemd service files
"""


def is_active(service: str) -> bool:
    """
    Checks whether or not a systemd securiphant service is active or not
    :param service: The service to check
    :return: True if active, else False
    """
    return systemctl_call(service, "status") == 0


def start_service(service: str):
    """
    Starts a service if it's not already running
    :param service: The service to start
    :return: None
    """
    if not is_active(service):
        systemctl_call(service, "start")


def stop_service(service: str):
    """
    Stops a service if it's running
    :param service: The service to stop
    :return: None
    """
    if is_active(service):
        systemctl_call(service, "stop")


def systemctl_call(service: str, mode: str) -> int:
    """
    Calls a systemctl command for a service
    :param service: The service for which to call the command
    :param mode: The command mode (ex: start or stop)
    :return: The status code of the call
    """
    state = call(
        [
            "systemctl", "--user",
            mode,
            "securiphant-{}.service".format(service)
        ],
        stderr=PIPE,
        stdout=PIPE
    )
    return state


def reload_daemon():
    """
    Reloads the systemd daemon
    :return: None
    """
    call(["systemctl", "--user", "daemon-reload"], stderr=PIPE, stdout=PIPE)
