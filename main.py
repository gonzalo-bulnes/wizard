import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from push_button import PushButton
from wizard import Wizard
from simulator import Simulator
from device import Device

# Magic values.
SEPARATOR = "separator"


class Main(QMainWindow):
    """The application main window."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()
        self._device_present = False
        self._device_locked = False

    def setupUI(self):
        self.setWindowTitle("Wizard Demo")
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.statusBar()

        appActions = self.__createAppActions()
        _addActions(self, appActions)

        layout = QVBoxLayout()
        self.centralWidget.setLayout(layout)

        device = Device()
        simulator = Simulator(device)
        wizard_launcher = QWidget()
        wizard = Wizard(device)

        layout.addWidget(wizard_launcher)
        layout.addWidget(simulator)

        # Wizard
        layout = QVBoxLayout()
        wizard_launcher.setLayout(layout)
        title = QLabel("<h1>Wizard</h1>")
        layout.addWidget(title)
        intro = QLabel()
        intro.setText("<p>This demo application allows to test a <b>Wizard</b>.</p><p>You can start the wizard using the button below, and simulate the insertion or removal of USB drives using the simulator.</p><p>USB drives can be inserted or removed at any time, try different combinations!</p>")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        start = PushButton(PushButton.TypeContained)
        start.setText("START WIZARD")
        start.clicked.connect(self.on_wizard_started)
        layout.addWidget(start)

        wizard.finished.connect(lambda: self.on_wizard_finished())

        self.start = start
        self.wizard = wizard
        self.device = device
        self.simulator = simulator

        
    def on_wizard_started(self):
        self.start.setEnabled(False)
        self.start.setText("WIZARD STARTED")
        self.wizard.show()

    def on_wizard_finished(self):
        self.start.setText("START WIZARD")
        self.start.setEnabled(True)
        self.wizard.restart()

    def closeEvent(self, event):
        self.wizard.close()
        super().closeEvent(event)

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
