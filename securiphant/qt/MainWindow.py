"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

from PyQt5.QtWidgets import QMainWindow
from securiphant.qt.generated.main import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    The Main Window of the application
    """

    def __init__(self):
        """
        Initializes the main window
        """
        super().__init__(None)
        self.setupUi(self)
        self.showFullScreen()
