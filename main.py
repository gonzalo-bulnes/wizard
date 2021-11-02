import os
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *  # type: ignore [misc]
from PyQt5.QtWidgets import *
from typing import NewType, NoReturn

# Magic values.
SEPARATOR = "separator"

FontName = NewType("FontName", str)

MONTSERRAT = FontName('Montserrat')

MColor = NewType("MColor", str)

PRIMARY = MColor("#1564bf")
PRIMARY_LIGHT = MColor("#5e91f2")
PRIMARY_DARK = MColor("#003b8e")
SECONDARY = MColor("#00e5ff")
SECONDARY_LIGHT = MColor("#6effff")
SECONDARY_DARK = MColor("#00b2cc")
WHITE = MColor("#ffffff")
BLACK = MColor("#000000")
ERROR = MColor("#9e1e63")

MButtonType = NewType("MButtonType", str)

CONTAINED = MButtonType("contained-2347")
TEXT = MButtonType("text-2143")

TranslatableString = NewType("TranslatableString", str)

class ButtonTypeNotImplemented(BaseException):
    pass

class Button(QPushButton):
    """A QPushButton with custom styles."""
    def __init__(self, materialType: MButtonType, text:TranslatableString, parent:QWidget = None) -> None:
        super().__init__(parent)
        self.setText(text)
        
        if materialType == CONTAINED:
            self.setProperty("type", "contained")
        elif materialType == TEXT:
            self.setProperty("type", "text")
        else:
            raise ButtonTypeNotImplemented

        self.setStyleSheet(f"""
            Button {{
                font-family: 'Montserrat';
                font-weight: 500;
                font-size: 18px;
                padding: 10px 20px;
                margin: 0;
                border-radius: 4px;
            }}

            [type=text] {{
                border: none;
                background-color: none;
                color: {SECONDARY};
            }}

            [type=text]:hover {{
                background-color: rgba(0, 0, 0, 0.08);
            }}
            [type=text]:hover:pressed {{
                background-color: rgba(0, 0, 0, 0.40);
            }}

            [type=contained] {{
                border: 1px solid {SECONDARY};
                background-color: {SECONDARY};
                color: {PRIMARY_DARK};
            }}
            [type=contained]:hover {{
                border: 1px solid rgba(0, 229, 255, 0.92);
                background-color: rgba(0, 229, 255, 0.92);
            }}
            [type=contained]:pressed {{
                border: 1px solid rgba(0, 229, 255, 0.6);
                background-color: rgba(0, 229, 255, 0.6);
                color: {PRIMARY_DARK};
            }}
        """)


class Main(QMainWindow):
    """The application main window."""
    def __init__(self, parent=None):
        super().__init__(parent)
        _loadFont(MONTSERRAT)
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("Widgets")
        #self.resize(800, 600)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        appActions = self.__createAppActions()
        _addActions(self, appActions)

        layout = QHBoxLayout()
        logIn = Button(CONTAINED, "SIGN IN")
        useOffline = Button(TEXT, "USE OFFLINE")
        layout.addWidget(logIn)
        layout.addWidget(useOffline)
        layout.addStretch()
        self.centralWidget.setLayout(layout)
        self.centralWidget.setStyleSheet(f"""
            QWidget {{
                background-color: {PRIMARY_DARK};
            }}
        """)

    def __createAppActions(self):
        quitAction = QAction("&Quit", self)
        quitAction.setIcon(QIcon.fromTheme("application-exit"))
        quitAction.setShortcut(QKeySequence.Quit)
        quitAction.triggered.connect(self.close)
        return [
                quitAction,
        ]

def _addActions(parent, actions):
    """Add actions to a menu or toolbar, add separator if action is None."""
    for action in actions:
        if action is SEPARATOR:
            action = QAction(parent)
            action.setSeparator(True)
        parent.addAction(action)

def _loadFont(name: FontName) -> None:
    dirname = os.path.dirname(__file__)
    directory = os.path.join(dirname, "vendor", name)
    for filename in os.listdir(directory):
        if filename.endswith(".ttf"):
            QFontDatabase.addApplicationFont(os.path.join(directory, filename))

app = QApplication(sys.argv)

# Periodically listen for Unix signals (e.g. SIGINT)
timer = QTimer()
timer.start(500)
timer.timeout.connect(lambda: None)

window = Main()
window.show()
sys.exit(app.exec())
