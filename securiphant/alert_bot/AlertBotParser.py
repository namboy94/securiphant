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
