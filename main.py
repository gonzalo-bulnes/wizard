import sys
from typing import NewType

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from push_button import PushButton

# Magic values.
SEPARATOR = "separator"


class Main(QMainWindow):
    """The application main window."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("Widgets")
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.statusBar()

        appActions = self.__createAppActions()
        _addActions(self, appActions)

        layout = QHBoxLayout()
        label = QLabel("Demo")
        layout.addWidget(label)

        # This is our button!
        button = PushButton()
        button.setText("SIGN IN")
        button.clicked.connect(lambda: self.statusBar().showMessage("Clicked!", 500))

        # Support buttons.
        disable = QPushButton("Disable button")
        layout.addWidget(disable)
        enable = QPushButton("Enable button")
        layout.addWidget(enable)
        disable.clicked.connect(lambda: button.setEnabled(False))
        enable.clicked.connect(lambda: button.setEnabled(True))

        layout.addWidget(button)
        self.centralWidget.setLayout(layout)

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

app = QApplication(sys.argv)

# Periodically listen for Unix signals (e.g. SIGINT)
timer = QTimer()
timer.start(500)
timer.timeout.connect(lambda: None)

window = Main()
window.show()
sys.exit(app.exec())
