"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

import time
from datetime import datetime
from threading import Thread
from PyQt5.QtWidgets import QMainWindow
from securiphant.qt.generated.main import Ui_MainWindow
from securiphant.systemd import is_active


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    The Main Window of the application
    """

    RED_BG = "background-color: rgb(255, 0, 0);"
    GREEN_BG = "background-color: rgb(0, 255, 0);"

    def __init__(self):
        """
        Initializes the main window
        """
        super().__init__(None)
        self.setupUi(self)
        self.showFullScreen()
        self.set_time()
        self.set_service_states()
        self.refresh_thread = Thread(target=self.refresh)
        self.refresh_thread.start()

    def refresh(self):
        """
        Periodically refreshes the UI
        :return: None
        """
        while True:
            self.set_time()
            self.set_service_states()
            time.sleep(0.5)

    def set_time(self):
        """
        Sets the time of day on the UI
        :return: None
        """
        now = datetime.now()
        self.hour_display.display(now.hour)
        self.minute_display.display(now.minute)
        self.second_display.display(now.second)
        self.date_display.setText(now.strftime("%Y-%m-%d"))

    def set_service_states(self):
        """
        Displays the states of securiphant systemd services on the UI
        :return: None
        """
        for service, widget in [
            ("alert-bot", self.alert_bot_state),
            ("check-door", self.check_door_state),
            ("check-nfc", self.check_nfc_state),
            ("display", self.display_state)
        ]:
            status = is_active(service)

            if status:
                widget.setStyleSheet(self.GREEN_BG)
            else:
                widget.setStyleSheet(self.RED_BG)
