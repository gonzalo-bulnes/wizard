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

        # This are our buttons!
        signIn = PushButton(PushButton.TypeContained)
        signIn.setText("SIGN IN")
        signIn.clicked.connect(lambda: self.statusBar().showMessage("Signed in!", 500))

        signUp = PushButton(PushButton.TypeOutlined)
        signUp.setText("SIGN UP")
        signUp.clicked.connect(lambda: self.statusBar().showMessage("Signed up!", 500))

        think = PushButton(PushButton.TypeText)
        think.setText("ASK ME TOMORROW")
        think.clicked.connect(lambda: self.statusBar().showMessage("Will ask tomorrow!", 500))

        # Support buttons.
        disableSignIn = QPushButton("Disable signIn")
        layout.addWidget(disableSignIn)
        enableSignIn = QPushButton("Enable signIn")
        layout.addWidget(enableSignIn)
        disableSignIn.clicked.connect(lambda: signIn.setEnabled(False))
        enableSignIn.clicked.connect(lambda: signIn.setEnabled(True))
        layout.addWidget(signIn)

        disableSignUp = QPushButton("Disable signUp")
        layout.addWidget(disableSignUp)
        enableSignUp = QPushButton("Enable signUp")
        layout.addWidget(enableSignUp)
        disableSignUp.clicked.connect(lambda: signUp.setEnabled(False))
        enableSignUp.clicked.connect(lambda: signUp.setEnabled(True))
        layout.addWidget(signUp)

        disableThink = QPushButton("Disable ask")
        layout.addWidget(disableThink)
        enableThink = QPushButton("Enable ask")
        layout.addWidget(enableThink)
        disableThink.clicked.connect(lambda: think.setEnabled(False))
        enableThink.clicked.connect(lambda: think.setEnabled(True))
        layout.addWidget(think)

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
