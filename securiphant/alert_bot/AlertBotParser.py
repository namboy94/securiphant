"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""
from typing import List

from kudubot.parsing.Command import Command
from kudubot.parsing.CommandParser import CommandParser


class AlertBotParser(CommandParser):
    """
    The Parser for the Alert Bot
    """

    @classmethod
    def name(cls) -> str:
        """
        :return: The name of the parser
        """
        return "securiphant_commands"

    @classmethod
    def commands(cls) -> List[Command]:
        """
        :return: The enabled commands for this bot
        """
        return [
            Command("init", [("key", str)]),
            Command("status", []),
            Command("photo", []),
            Command("video", [("seconds", int)]),
            Command("door_open_events", [("count", int)]),
            Command("arm", []),
            Command("false_alarm", []),
        ]
