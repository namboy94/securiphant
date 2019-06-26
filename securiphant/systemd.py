"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

from subprocess import call, PIPE


def is_active(service: str) -> bool:
    """
    Checks whether or not a systemd securiphant service is active or not
    :param service: The service to check
    :return: True if active, else False
    """
    state = call(
        [
            "systemctl", "--user",
            "status",
            "securiphant-{}.service".format(service)
        ],
        stderr=PIPE,
        stdout=PIPE
    )
    return state == 0


def start_service(service: str):
    """
    Starts a service if it's not already running
    :param service: The service to start
    :return: None
    """
    if not is_active(service):
        call(
            [
                "systemctl", "--user",
                "start",
                "securiphant-{}.service".format(service)
            ],
            stderr=PIPE,
            stdout=PIPE
        )
