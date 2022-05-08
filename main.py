import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from push_button import PushButton
from wizard import Wizard

# Magic values.
SEPARATOR = "separator"


class Main(QMainWindow):
    """The application main window."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()
        self._device_present = False
        self._device_adequate = False

    def setupUI(self):
        self.setWindowTitle("Wizard Demo")
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.statusBar()

        appActions = self.__createAppActions()
        _addActions(self, appActions)

        layout = QVBoxLayout()
        self.centralWidget.setLayout(layout)

        simulator = QWidget()
        wizard_launcher = QWidget()
        wizard = Wizard(self.device_present, self.device_adequate)
        
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

        # Simulator
        layout = QVBoxLayout()
        simulator.setLayout(layout)
        title = QLabel("<h1>USB Device Simulator</h1>")
        layout.addWidget(title)
        status = QLabel("<p>Loading...</p>")
        status.setWordWrap(True)
        layout.addWidget(status)

        insertAdequateDevice = PushButton(PushButton.TypeContained)
        insertAdequateDevice.setText("INSERT ADEQUATE USB DRIVE")
        insertAdequateDevice.clicked.connect(self.on_adequate_device_inserted)
        layout.addWidget(insertAdequateDevice)

        insertInadequateDevice = PushButton(PushButton.TypeOutlined)
        insertInadequateDevice.setText("INSERT INADEQUATE USB DRIVE")
        insertInadequateDevice.clicked.connect(self.on_inadequate_device_inserted)
        layout.addWidget(insertInadequateDevice)

        removeDevice = PushButton(PushButton.TypeText)
        removeDevice.setText("REMOVE USB DRIVE")
        removeDevice.clicked.connect(self.on_device_removed)
        layout.addWidget(removeDevice)

        layout.addStretch()

        self.insertAdequateDevice = insertAdequateDevice
        self.insertInadequateDevice = insertInadequateDevice
        self.removeDevice = removeDevice
        self.status = status

        self.on_device_removed()
        
    def device_present(self):
        return self._device_present

    def device_adequate(self):
        return self._device_adequate

    def on_adequate_device_inserted(self):
        self._device_present = True
        self._device_adequate = True
        self.insertAdequateDevice.setEnabled(False)
        self.insertAdequateDevice.hide()
        self.insertInadequateDevice.setEnabled(False)
        self.insertInadequateDevice.hide()
        self.removeDevice.show()
        self.removeDevice.setEnabled(True)
        self.status.setText("<p>An adequate USB drive is present.</p>")

    def on_inadequate_device_inserted(self):
        self._device_present = True
        self._device_adequate = False
        self.insertAdequateDevice.setEnabled(False)
        self.insertAdequateDevice.hide()
        self.insertInadequateDevice.setEnabled(False)
        self.insertInadequateDevice.hide()
        self.removeDevice.show()
        self.removeDevice.setEnabled(True)
        self.status.setText("<p>A USB drive is <b>present</b>, but it is <b>not encrypted</b>, or is otherwise inadequate.</p>")

    def on_device_removed(self):
        self._device_present = False
        self._device_adequate = False
        self.removeDevice.setEnabled(False)
        self.removeDevice.hide()
        self.status.setText("<b>No USB drive is present.</b>")
        self.insertAdequateDevice.show()
        self.insertAdequateDevice.setEnabled(True)
        self.insertInadequateDevice.show()
        self.insertInadequateDevice.setEnabled(True)

    def on_wizard_started(self):
        self.start.setEnabled(False)
        self.start.setText("WIZARD STARTED")
        self.wizard.show()

    def on_wizard_finished(self):
        self.start.setText("START WIZARD")
        self.start.setEnabled(True)

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
