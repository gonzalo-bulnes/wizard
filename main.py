import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from buttons import PushButton
from wizard import ThemedWizard as Wizard
from device import Device, Simulator as DeviceSimulator
import export

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
        device_simulator = DeviceSimulator(device)

        export_service = export.Service(device)
        export_simulator = export.Simulator(export_service)

        wizard_launcher = QWidget()
        wizard = Wizard(device, export_service)

        layout.addWidget(wizard_launcher)
        layout.addWidget(device_simulator)
        layout.addWidget(export_simulator)
        layout.addStretch(1)

        # Wizard
        layout = QVBoxLayout()
        wizard_launcher.setLayout(layout)
        title = QLabel("<h1>Wizard</h1>")
        layout.addWidget(title)
        intro = QLabel()
        intro.setText("<p>This demo application allows to test a <b>Wizard</b>.</p><p>You can start the wizard using the button below, and simulate the insertion or removal of USB drives using the simulator.</p><p>USB drives can be inserted or removed at any time, try different combinations!</p><p>Once you're ready to export, you can still use the device simulator! And you can also use the export simulator to try a wider variety of scenarios.</p><p>Combine things the way you want, there are bonus points for breaking the wizard.</p>")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        layout.setSizeConstraint(QLayout.SetFixedSize)

        start = PushButton(PushButton.TypeContained)
        start.setText("START WIZARD")
        start.clicked.connect(self.on_wizard_started)
        layout.addWidget(start)

        wizard.finished.connect(lambda: self.on_wizard_finished())

        self.start = start
        self.wizard = wizard
        self.device = device
        self.device_simulator = device_simulator

        
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
