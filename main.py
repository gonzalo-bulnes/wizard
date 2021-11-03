import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# Magic values.
SEPARATOR = "separator"

class PushButtonState(QWidget):
    """The state of a button for styling purposes.

    stateDiagram-v2
    [*] --> Enabled
    Enabled --> Disabled: disable
    Disabled --> Enabled: enable

    state Enabled {
        [*] --> NotHover
        NotHover --> Hover: HoverEnter
        Hover --> NotHover: HoverLeave
        Hover --> Pressed: MouseButtonDown
        --
        [*] --> NotFocus
        NotFocus --> Focus: FocusIn
        Focus --> NotFocus: FocusOut
        Focus --> Pressed: KeyPress
        --
        [*] --> NotPressed
        Pressed --> NotPressed
    }
    """

    _disableActionTriggered = pyqtSignal()
    _enableActionTriggered = pyqtSignal()
    _hoverActionTriggered = pyqtSignal()
    _toggleActionTriggered = pyqtSignal()

    _hoverInEventTriggered = pyqtSignal()
    _hoverOutEventTriggered = pyqtSignal()
    _focusEventTriggered = pyqtSignal()
    _blurEventTriggered = pyqtSignal()
    _mousePressEventTriggered = pyqtSignal()
    _mouseReleaseEventTriggered = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.machine = QStateMachine()

        self.enabled = QState(QState.ParallelStates)
        self.disabled = QState()
        self.enabled.addTransition(self._disableActionTriggered, self.disabled)
        self.enabled.addTransition(self._toggleActionTriggered, self.disabled)
        self.disabled.addTransition(self._enableActionTriggered, self.enabled)
        self.disabled.addTransition(self._toggleActionTriggered, self.enabled)

        self.machine.addState(self.enabled)
        self.machine.addState(self.disabled)
        self.machine.setInitialState(self.enabled)

        self.hover = QState(self.enabled)
        self.hoverOn = QState(self.hover)
        self.hoverOff = QState(self.hover)
        self.hover.setInitialState(self.hoverOff)
        self.hoverOn.addTransition(self._hoverOutEventTriggered, self.hoverOff)
        self.hoverOff.addTransition(self._hoverInEventTriggered, self.hoverOn)

        self.focus = QState(self.enabled)
        self.focusOn = QState(self.focus)
        self.focusOff = QState(self.focus)
        self.focus.setInitialState(self.focusOff)
        self.focusOn.addTransition(self._blurEventTriggered, self.focusOff)
        self.focusOff.addTransition(self._focusEventTriggered, self.focusOn)
        
        self.pressed = QState(self.enabled)
        self.pressedOn = QState(self.pressed)
        self.pressedOff = QState(self.pressed)
        self.pressed.setInitialState(self.pressedOff)
        self.pressedOn.addTransition(self._mouseReleaseEventTriggered, self.pressedOff)
        self.pressedOff.addTransition(self._mousePressEventTriggered, self.pressedOn)

        self.machine.start()

    def disable(self) -> None:
        self._disableActionTriggered.emit()

    def enable(self) -> None:
        self._enableActionTriggered.emit()

    def toggle(self) -> None:
        self._toggleActionTriggered.emit()

    def hoverIn(self) -> None:
        self._hoverInEventTriggered.emit()

    def hoverOut(self) -> None:
        self._hoverOutEventTriggered.emit()

    def focusIn(self) -> None:
        self._focusEventTriggered.emit()

    def blur(self) -> None:
        self._blurEventTriggered.emit()

    def press(self) -> None:
        self._mousePressEventTriggered.emit()

    def release(self) -> None:
        self._mouseReleaseEventTriggered.emit()

class PushButton(QPushButton):
    """A QPushButton with custom styles."""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.state = PushButtonState()

        self.styles = f"""
            * {{
                border: none;
                border-radius: 4px;
                font: 500 18px 'Monsterrat';
                outline: none;
                padding: .5em 1em;
            }}

            [state=enabled] {{
                background-color: #6000ee;
                color: #ffffff;
            }}

            [state=hover] {{
                background-color: #6e14ef;
                color: white;
            }}

            [state=focus] {{
                background-color: #873df2;
                color: white;
            }}

            [state=pressed] {{
                background-color: #9452f3;
                color: white;
            }}

            [state=disabled] {{
                background-color: #cccccc;
                color: #838383;
            }}
        """
        self.setStyleSheet(self.styles)

        self.state.enabled.entered.connect(lambda: self.setProperty("state", "enabled"))
        self.state.enabled.entered.connect(lambda: self.setText("ENABLED"))
        self.state.enabled.entered.connect(lambda: self.setElevation(2))
        self.state.enabled.entered.connect(lambda: self.setStyleSheet(self.styles))

        self.state.disabled.entered.connect(lambda: self.setProperty("state", "disabled"))
        self.state.disabled.entered.connect(lambda: self.setText("DISABLED"))
        self.state.disabled.entered.connect(lambda: self.setElevation(0))
        self.state.disabled.entered.connect(lambda: self.setStyleSheet(self.styles))

        self.state.hoverOn.entered.connect(lambda: self.setProperty("state", "hover"))
        self.state.hoverOn.entered.connect(lambda: self.setText("HOVER"))
        self.state.hoverOn.entered.connect(lambda: self.setElevation(4))
        self.state.hoverOn.entered.connect(lambda: self.setStyleSheet(self.styles))

        self.state.focusOn.entered.connect(lambda: self.setProperty("state", "focus"))
        self.state.focusOn.entered.connect(lambda: self.setText("FOCUS"))
        self.state.focusOn.entered.connect(lambda: self.setElevation(2))
        self.state.focusOn.entered.connect(lambda: self.setStyleSheet(self.styles))

        self.state.pressedOn.entered.connect(lambda: self.setProperty("state", "pressed"))
        self.state.pressedOn.entered.connect(lambda: self.setText("PRESSED"))
        self.state.pressedOn.entered.connect(lambda: self.setElevation(8))
        self.state.pressedOn.entered.connect(lambda: self.setStyleSheet(self.styles))

        #self.clicked.connect(self.state.toggle)
        self.clicked.connect(self.status)

    def setElevation(self, elevation: int) -> None:
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(0, 2*elevation)
        shadow.setBlurRadius(5*elevation)
        shadow.setColor(QColor("#44000000"))
        self.setGraphicsEffect(shadow)
        self.update()
        
    def status(self):
        #print(self.property("state"))
        pass

    def event(self, e: QEvent) -> bool:
        if type(e) is QHoverEvent:
            if e.oldPos() == QPoint(-1, -1):
                self.setProperty("state", "hover")
                self.state.hoverIn()
                self.setStyleSheet(self.styles)
            if e.pos() == QPoint(-1, -1):
                self.setProperty("state", "enabled")
                self.state.hoverOut()
                self.setStyleSheet(self.styles)
        if type(e) is QFocusEvent:
            if e.gotFocus():
                self.setProperty("state", "focus")
                self.state.focusIn()
                self.setStyleSheet(self.styles)
            if e.lostFocus():
                self.setProperty("state", "enabled")
                self.state.blur()
                self.setStyleSheet(self.styles)
        return super().event(e)

    def mousePressEvent(self, e: QEvent) -> bool:
        self.setProperty("state", "pressed")
        self.state.press()
        self.setStyleSheet(self.styles)
        return super().mousePressEvent(e)


class Main(QMainWindow):
    """The application main window."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("Widgets")
        self.resize(800, 600)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        appActions = self.__createAppActions()
        _addActions(self, appActions)

        layout = QHBoxLayout()
        b = QPushButton("OK")
        layout.addWidget(b)
        label = QLabel("Hello, world!")
        layout.addWidget(label)
        button = PushButton()
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
