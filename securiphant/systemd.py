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
