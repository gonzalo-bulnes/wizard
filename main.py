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

AVATAR_SIZE = 40

class UserMenu(QMenu):

    def __init__(self, parent=None):
        title = "journalist"
        super().__init__(title, parent)

        self.setStyleSheet("""
            QMenu {
                border: 0;
                spacing: 0;
            }
        """)
        action = self.menuAction()
        pix = QStyle.SP_TitleBarUnshadeButton
        icon = self.style().standardIcon(pix)
        #action.setIcon(icon)
        self.addAction("Logout")

    def showEvent(self, event):
        self.move(QPoint(self.pos().x() - AVATAR_SIZE, self.pos().y()))
        super().showEvent(event)

    def ignore(self):
        pixmap = QPixmap()
        painter = QPainter(pixmap)
        painter.setFont(QFont("Arial"))
        painter.drawText(QRect(), Qt.AlignCenter, "HELLO")

class Avatar(QLabel):
    def __init__(self, menu, parent=None):
        super().__init__(parent)
        self.menu = menu
        self.setText("JZ")
        self.setStyleSheet("""
            QLabel {
                background-color: skyblue;
                border-radius: 20px;
                font-size: 20;
            }
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(QSize(AVATAR_SIZE, AVATAR_SIZE))

    def mousePressEvent(self, event):
        menu_position = self.parent().mapToGlobal(QPoint(AVATAR_SIZE, AVATAR_SIZE+3))
        self.menu.exec(menu_position)


ICON_SIZE = 10


class Arrow(QLabel):
    def __init__(self, menu, parent=None):
        super().__init__(parent)
        self.menu = menu

        pix = QStyle.SP_TitleBarUnshadeButton
        icon = self.style().standardIcon(pix)

        self.setPixmap(icon.pixmap(QSize(ICON_SIZE, ICON_SIZE)))
        self.setFixedSize(QSize(ICON_SIZE + 8, AVATAR_SIZE + 6))
        self.setAlignment(Qt.AlignCenter)

    def mousePressEvent(self, event):
        menu_position = self.parent().mapToGlobal(QPoint(AVATAR_SIZE, AVATAR_SIZE+3))
        self.menu.exec(menu_position)

class UserMenuBar(QMenuBar):

    def __init__(self, parent=None):
        super().__init__(parent)

        menu = UserMenu(self)
        self.addMenu(menu)

        self.setCornerWidget(Avatar(menu), Qt.TopLeftCorner)
        self.setCornerWidget(Arrow(menu), Qt.TopRightCorner)

        self.setStyleSheet("""
            QMenuBar {
                border: 1px solid skyblue;
                spacing: 0;
                padding: 0 4px 0 4px;
                border-radius: 24px;
            }
            QMenuBar::item {
                font-size: 24px; /* FIXME: doesn't have any effect */
                padding: 12px 0 12px 8px;
                border: 0;
            }
            QMenuBar::item:selected {
                border: 0;
            }
            QMenuBar::item:pressed {
                border: 0;
            }
        """)

        self.setSizePolicy(QSizePolicy())

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

        user_menu_bar = UserMenuBar()
        layout.addWidget(user_menu_bar)
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
        self.user_menu_bar = user_menu_bar

        
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
