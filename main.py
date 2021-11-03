import sys
from typing import NewType

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# Magic values.
SEPARATOR = "separator"

class PushButtonState(QWidget):
    """The state of a button for styling purposes.

    stateDiagram-v2
      [*] --> enabled
      enabled --> disabled: disable
      disabled --> enabled: enable

      state enabled {
        resting --> hoverFromResting: HoverIn
        hoverFromResting --> resting: HoverOut

        resting --> focusFromResting: FocusIn
        focusFromResting --> resting: FocusOut

        hoverFromResting --> pressedFromHoverFromResting: MousePress
        pressedFromHoverFromResting --> hoverFromResting: MouseRelease

        focusFromResting --> pressedFromFocusFromResting: MousePress
        pressedFromFocusFromResting --> focusFromResting: MouseRelease

        focusFromResting --> hoverFromFocusFromResting: FocusOut
        hoverFromFocusFromResting --> focusFromResting: FocusIn

        hoverFromFocusFromResting --> pressedFromHoverFromFocusFromResting: MousePress
        pressedFromHoverFromFocusFromResting --> hoverFromFocusFromResting: MouseRelease
      }
    """

    _disableActionTriggered = pyqtSignal()
    _enableActionTriggered = pyqtSignal()

    _hoverInEventTriggered = pyqtSignal()
    _hoverOutEventTriggered = pyqtSignal()
    _focusInEventTriggered = pyqtSignal()
    _focusOutEventTriggered = pyqtSignal()
    _mousePressEventTriggered = pyqtSignal()
    _mouseReleaseEventTriggered = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._machine = QStateMachine()

        self.enabled = QState()
        self.disabled = QState()
        self.enabled.addTransition(self._disableActionTriggered, self.disabled)
        self.disabled.addTransition(self._enableActionTriggered, self.enabled)

        self._machine.addState(self.enabled)
        self._machine.addState(self.disabled)
        self._machine.setInitialState(self.enabled)

        self.resting = QState(self.enabled)
        self.enabled.setInitialState(self.resting)

        self.hoverFromResting = QState(self.enabled)
        self.pressedFromHoverFromResting = QState(self.enabled)
        self.focusFromResting = QState(self.enabled)
        self.pressedFromFocusFromResting = QState(self.enabled)
        self.hoverFromFocusFromResting = QState(self.enabled)
        self.pressedFromHoverFromFocusFromResting = QState(self.enabled)

        self.resting.addTransition(self._hoverInEventTriggered, self.hoverFromResting)
        self.hoverFromResting.addTransition(self._hoverOutEventTriggered, self.resting)
        self.hoverFromResting.addTransition(self._mousePressEventTriggered, self.pressedFromHoverFromResting)
        self.pressedFromHoverFromResting.addTransition(self._mouseReleaseEventTriggered, self.hoverFromResting)

        self.resting.addTransition(self._focusInEventTriggered, self.focusFromResting)
        self.focusFromResting.addTransition(self._focusOutEventTriggered, self.resting)
        self.focusFromResting.addTransition(self._mousePressEventTriggered, self.pressedFromFocusFromResting)
        self.pressedFromFocusFromResting.addTransition(self._mouseReleaseEventTriggered, self.focusFromResting)

        self.focusFromResting.addTransition(self._hoverInEventTriggered, self.hoverFromFocusFromResting)
        self.hoverFromFocusFromResting.addTransition(self._hoverOutEventTriggered, self.focusFromResting)

        self.hoverFromFocusFromResting.addTransition(self._mousePressEventTriggered, self.pressedFromHoverFromFocusFromResting)
        self.pressedFromHoverFromFocusFromResting.addTransition(self._mouseReleaseEventTriggered, self.hoverFromFocusFromResting) 

        self._machine.start()

    def disable(self) -> None:
        self._disableActionTriggered.emit()

    def enable(self) -> None:
        self._enableActionTriggered.emit()

    def hoverIn(self) -> None:
        self._hoverInEventTriggered.emit()

    def hoverOut(self) -> None:
        self._hoverOutEventTriggered.emit()

    def focusIn(self) -> None:
        self._focusInEventTriggered.emit()

    def focusOut(self) -> None:
        self._focusOutEventTriggered.emit()

    def press(self) -> None:
        self._mousePressEventTriggered.emit()

    def release(self) -> None:
        self._mouseReleaseEventTriggered.emit()

Elevation = NewType("Elevation", int)

class PushButton(QPushButton):
    """A QPushButton with custom styles."""

    # See Material Design 2 diagram of default elevation values.
    # https://material.io/design/environment/elevation.html#default-elevations
    ElevationNone = Elevation(0)
    ElevationLow = Elevation(2)
    ElevationMedium = Elevation(4)
    ElevationHigh = Elevation(8)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.state = PushButtonState()

        self.styles = f"""
            * {{
                border: none;
                border-radius: 6px;
                font: 500 18px 'Monsterrat';
                outline: none;
                padding: .6em 1em;
            }}

            .enabled {{
                background-color: #6000ee;
                color: #ffffff;
            }}

            .hover {{
                background-color: #6e14ef;
                color: white;
            }}

            .focus {{
                background-color: #873df2;
                color: white;
            }}

            .pressed {{
                background-color: #9452f3;
                color: white;
            }}

            .disabled {{
                background-color: #cccccc;
                color: #838383;
            }}
        """
        self.setStyleSheet(self.styles)

        self.state.resting.entered.connect(lambda: self.setProperty("class", "enabled"))
        self.state.resting.entered.connect(lambda: self.setText("ENABLED"))
        self.state.resting.entered.connect(lambda: self.setElevation(self.ElevationLow))
        self.state.resting.entered.connect(lambda: self.setStyleSheet(self.styles))

        self.state.disabled.entered.connect(lambda: self.setProperty("class", "disabled"))
        self.state.disabled.entered.connect(lambda: self.setText("DISABLED"))
        self.state.disabled.entered.connect(lambda: self.setElevation(self.ElevationNone))
        self.state.disabled.entered.connect(lambda: self.setStyleSheet(self.styles))

        self.state.hoverFromResting.entered.connect(lambda: self.setProperty("class", "hover"))
        self.state.hoverFromResting.entered.connect(lambda: self.setText("HOVER"))
        self.state.hoverFromResting.entered.connect(lambda: self.setElevation(self.ElevationMedium))
        self.state.hoverFromResting.entered.connect(lambda: self.setStyleSheet(self.styles))

        self.state.hoverFromFocusFromResting.entered.connect(lambda: self.setProperty("class", "hover"))
        self.state.hoverFromFocusFromResting.entered.connect(lambda: self.setText("HOVER"))
        self.state.hoverFromFocusFromResting.entered.connect(lambda: self.setElevation(self.ElevationMedium))
        self.state.hoverFromFocusFromResting.entered.connect(lambda: self.setStyleSheet(self.styles))

        self.state.focusFromResting.entered.connect(lambda: self.setProperty("class", "focus"))
        self.state.focusFromResting.entered.connect(lambda: self.setText("FOCUSED"))
        self.state.focusFromResting.entered.connect(lambda: self.setElevation(self.ElevationLow))
        self.state.focusFromResting.entered.connect(lambda: self.setStyleSheet(self.styles))

        self.state.pressedFromHoverFromResting.entered.connect(lambda: self.setProperty("class", "pressed"))
        self.state.pressedFromHoverFromResting.entered.connect(lambda: self.setText("PRESSED"))
        self.state.pressedFromHoverFromResting.entered.connect(lambda: self.setElevation(self.ElevationHigh))
        self.state.pressedFromHoverFromResting.entered.connect(lambda: self.setStyleSheet(self.styles))

        self.state.pressedFromFocusFromResting.entered.connect(lambda: self.setProperty("class", "pressed"))
        self.state.pressedFromFocusFromResting.entered.connect(lambda: self.setText("PRESSED"))
        self.state.pressedFromFocusFromResting.entered.connect(lambda: self.setElevation(self.ElevationHigh))
        self.state.pressedFromFocusFromResting.entered.connect(lambda: self.setStyleSheet(self.styles))

        self.state.pressedFromHoverFromFocusFromResting.entered.connect(lambda: self.setProperty("class", "pressed"))
        self.state.pressedFromHoverFromFocusFromResting.entered.connect(lambda: self.setText("PRESSED"))
        self.state.pressedFromHoverFromFocusFromResting.entered.connect(lambda: self.setElevation(self.ElevationHigh))
        self.state.pressedFromHoverFromFocusFromResting.entered.connect(lambda: self.setStyleSheet(self.styles))

    def disable(self) -> None:
        self.state.disable()

    def setElevation(self, value: Elevation) -> None:
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(0, 1.5*value)
        shadow.setBlurRadius(4*value)
        shadow.setColor(QColor("#44000000"))
        self.setGraphicsEffect(shadow)
        self.update()
        
    def event(self, e: QEvent) -> bool:
        if type(e) is QHoverEvent:
            if e.oldPos() == QPoint(-1, -1):
                self.state.hoverIn()
            if e.pos() == QPoint(-1, -1):
                self.state.hoverOut()
        if type(e) is QFocusEvent:
            if e.gotFocus():
                self.state.focusIn()
            if e.lostFocus():
                self.state.focusOut()
        return super().event(e)

    def keyPressEvent(self, e: QEvent) -> bool:
        if e.key() == Qt.Key_Space:
            self.state.press()
        return super().keyPressEvent(e)

    def keyReleaseEvent(self, e: QEvent) -> bool:
        if e.key() == Qt.Key_Space:
            self.state.release()
        return super().keyReleaseEvent(e)

    def mousePressEvent(self, e: QEvent) -> bool:
        if e.button() == Qt.LeftButton:
            self.state.press()
        return super().mousePressEvent(e)

    def mouseReleaseEvent(self, e: QEvent) -> bool:
        self.state.release()
        return super().mouseReleaseEvent(e)

class Main(QMainWindow):
    """The application main window."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("Widgets")
        #self.resize(800, 600)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        appActions = self.__createAppActions()
        _addActions(self, appActions)

        layout = QHBoxLayout()
        label = QLabel("Hello, world!")
        layout.addWidget(label)
        b = QPushButton("Disable")
        layout.addWidget(b)
        button = PushButton()
        button.clicked.connect(lambda: print("clicked"))
        b.clicked.connect(lambda: button.disable())
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
