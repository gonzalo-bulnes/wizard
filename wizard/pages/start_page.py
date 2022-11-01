import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class StartPage(QWizardPage):
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Disclaimer")

        content = QLabel("Please be aware that exporting files carries some <b>risks</b>.")
        content.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(content)
        self.setLayout(layout)

        dirname = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(dirname, "page.css"), "r") as stylesheet:
            self.setStyleSheet(stylesheet.read())
