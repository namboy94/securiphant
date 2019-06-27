"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

import time
from datetime import datetime
from typing import List, Optional
from bokkichat.connection.Connection import Connection
from bokkichat.entities.message.Message import Message
from bokkichat.entities.message.TextMessage import TextMessage
from bokkichat.entities.message.MediaMessage import MediaMessage, MediaType
from kudubot.Bot import Bot
from kudubot.db.Address import Address as Address
from kudubot.parsing.CommandParser import CommandParser
from securiphant.db import uri
from securiphant.config import load_config
from securiphant.db.states.BooleanState import BooleanState
from securiphant.webcam import record_video
from securiphant.alert_bot.AlertBotParser import AlertBotParser


class AlertBot(Bot):
    """
    A kudubot implementation that monitors the database values and takes
    appropriate actions.
    The core functionality includes video recording of unauthorized people
    entering the secured room
    """

    def __init__(
            self,
            connection: Connection,
            location: str,
            _: Optional[str] = None
    ):
        """
        Initializes the bot
        :param connection: The connection the bot should use
        :param location: The location of config and DB files
        :param _: The database URI will always be the same as the main
                  securiphant sqlite database
        """
        super().__init__(connection, location, uri)
        self.owner_address = Address(
            id=-1, address=load_config()["telegram_address"]
        )

    def on_msg(self, message: Message, address: Address):
        """
        Responds to messages from the user.
        Only messages of the owner of the securiphant instance should ever
        be taken into consideration
        :param message: The received message
        :param address: The address of the message's sender
        :return: None
        """
        db_session = self.create_db_session()

        parsed = self.parse(message)
        if parsed is None:
            return
        _, command, args = parsed

        if address.address != self.owner_address.address:
            reply = message.make_reply()  # type: TextMessage
            reply.body = "Unauthorized"
            self.connection.send(reply)
            return

        if command == "false_alarm":
            door_opened = self.db_session.query(BooleanState)\
                .filter_by(key="door_opened").first()
            door_opened.value = False
            db_session.commit()
        elif command == "video":
            tempfile = "/tmp/securiphant-manual-video.mp4"
            record_video(args["seconds"], tempfile)
            timestamp = datetime.now().strftime("```%Y-%m-%d:%H-%M-%S```")
            self.send_video(tempfile, timestamp)

    @classmethod
    def name(cls) -> str:
        """
        :return: The name of the bot
        """
        return "securiphant"

    @classmethod
    def parsers(cls) -> List[CommandParser]:
        """
        :return: A list of command parser for this bot
        """
        return [AlertBotParser()]

    def notify(self, message: str):
        """
        Sends a message to the owner
        :param message: The message text to send
        :return: None
        """
        message = TextMessage(
            self.connection.address,
            self.owner_address,
            message
        )
        self.connection.send(message)

    def send_video(self, video_file: str, caption: str):
        """
        Sends a video file to the owner
        :param video_file: The video file to send
        :param caption: The caption to attach
        :return: None
        """
        with open(video_file, "rb") as f:
            data = f.read()
        media = MediaMessage(
            self.connection.address,
            self.owner_address,
            MediaType.VIDEO,
            data,
            caption
        )
        self.connection.send(media)

    def run_in_bg(self):
        """
        The logic of the background thread monitoring the database values
        :return: None
        """
        waiting_for_authorization = False
        tempfile = "/tmp/securiphant-recording.mp4"

        while True:
            time.sleep(1)

            db_session = self.create_db_session()
            door_opened = db_session.query(BooleanState)\
                .filter_by(key="door_opened").first()
            user_authorized = db_session.query(BooleanState)\
                .filter_by(key="user_authorized").first()
            print(door_opened.value)
            print(user_authorized.value)

            if not door_opened.value:
                continue

            else:
                if user_authorized.value:
                    door_opened.value = False
                    db_session.commit()
                elif waiting_for_authorization:
                    self.send_video(tempfile, "A break-in has been detected!")
                    record_video(30, tempfile)
                else:
                    waiting_for_authorization = True
                    record_video(15, tempfile)
