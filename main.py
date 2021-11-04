import sys
from typing import NewType

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# Magic values.
SEPARATOR = "separator"

class PushButtonState(QWidget):
    """The state of a button for styling purposes.

    There should be no need for you to use this class directly.

    This class described the behavior of a button. A disabled button doesn't
    react to user interaction. An enabled button can be in a resting state,
    be subject to hover, focus, or be pressed.

    These states follow the Material Design 2 guidelines.
    See https://material.io/components/buttons.html


    Paste the following state chart in https://mermaid.live for
    a visual representation of the behavior implemented by this class!

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

    _keyPressEventTriggered = pyqtSignal()  # Should not be necessary. Bug workaround.

    def __init__(self, button: "PushButton") -> None:
        super().__init__()

        self.button = button

        # Declare the state chart described in the docstring.
        # See https://doc.qt.io/qt-5/statemachine-api.html
        #
        # This is a very declarative exercise.
        # The state names are part of the API of this class,
        # as well as the event handling functions.
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

        QEventTransition(self.button, QEvent.HoverEnter, self.resting).setTargetState(self.hoverFromResting)
        QEventTransition(self.button, QEvent.HoverLeave, self.hoverFromResting).setTargetState(self.resting)

        QEventTransition(self.button, QEvent.MouseButtonPress, self.hoverFromResting).setTargetState(self.pressedFromHoverFromResting)
        QEventTransition(self.button, QEvent.MouseButtonRelease, self.pressedFromHoverFromResting).setTargetState(self.hoverFromResting)
        QEventTransition(self.button, QEvent.KeyPress, self.hoverFromResting).setTargetState(self.pressedFromHoverFromResting)
        QEventTransition(self.button, QEvent.KeyRelease, self.pressedFromHoverFromResting).setTargetState(self.hoverFromResting)

        QEventTransition(self.button, QEvent.FocusIn, self.resting).setTargetState(self.focusFromResting)
        QEventTransition(self.button, QEvent.FocusOut, self.focusFromResting).setTargetState(self.resting)

        QEventTransition(self.button, QEvent.MouseButtonPress, self.focusFromResting).setTargetState(self.pressedFromFocusFromResting)
        QEventTransition(self.button, QEvent.MouseButtonRelease, self.pressedFromFocusFromResting).setTargetState(self.focusFromResting)

        # Bug: causes a pressed state to be triggered when tabbing out.
        #QEventTransition(self.button, QEvent.KeyPress, self.focusFromResting).setTargetState(self.pressedFromFocusFromResting)
        self.focusFromResting.addTransition(self._keyPressEventTriggered, self.pressedFromFocusFromResting) 
        QEventTransition(self.button, QEvent.KeyRelease, self.pressedFromFocusFromResting).setTargetState(self.focusFromResting)

        QEventTransition(self.button, QEvent.HoverEnter, self.focusFromResting).setTargetState(self.hoverFromFocusFromResting)
        QEventTransition(self.button, QEvent.HoverLeave, self.hoverFromFocusFromResting).setTargetState(self.focusFromResting)

        QEventTransition(self.button, QEvent.MouseButtonPress, self.hoverFromFocusFromResting).setTargetState(self.pressedFromHoverFromFocusFromResting)
        QEventTransition(self.button, QEvent.MouseButtonRelease, self.pressedFromHoverFromFocusFromResting).setTargetState(self.hoverFromFocusFromResting)
        QEventTransition(self.button, QEvent.KeyPress, self.hoverFromFocusFromResting).setTargetState(self.pressedFromHoverFromFocusFromResting)
        QEventTransition(self.button, QEvent.KeyRelease, self.pressedFromHoverFromFocusFromResting).setTargetState(self.hoverFromFocusFromResting)

        self._machine.start()

    def disable(self) -> None:
        self._disableActionTriggered.emit()

    def enable(self) -> None:
        self._enableActionTriggered.emit()

    def postEvent(self, e: QEvent) -> None:
        self._machine.postEvent(QEvent(e))

    # Should not be necessary. Bug workaround.
    def press(self) -> None:
        self._keyPressEventTriggered.emit()

class PushButton(QPushButton):
    """
    A QPushButton with custom styles.

    While this widget looks and behaves according to the Material Design 2 guidelines,
    the custom behavior was implemented to avoid obstructing the QPushButton API.
    This means all accessibility features of a QPushButton should be available.

    For example, this button can be focused using your usual operating system
    keyboard shortcuts (typically by using TAB or arrow keys), and activated
    accordingly (typically by pressing the Space bar).

    This widget also emits all the events that a regular QPushButton emits.
    """

    # You shouldn't need to refer to these states outside this class.
    State = NewType("State", str)
    StateEnabled = State("enabled")
    StateHover = State("hover")
    StateFocus = State("focus")
    StatePressed = State("pressed")
    StateDisabled = State("disabled")

    # You shouldn't need to refer to these elevations outside this class.
    # See Material Design 2 diagram of default elevation values.
    # https://material.io/design/environment/elevation.html#default-elevations
    Elevation = NewType("Elevation", int)
    ElevationNone = Elevation(0)
    ElevationLow = Elevation(2)
    ElevationMedium = Elevation(4)
    ElevationHigh = Elevation(8)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.state = PushButtonState(self)
        self.debug = False

        self.setProperty("class", "pushButton")
        self.styles = """
            .pushButton {
                background-color: #6000ee;
                border: none;
                border-radius: 6px;
                color: #ffffff;
                font: 500 18px 'Monsterrat';
                margin-bottom: 1em;
                outline: none;
                padding: .6em 1em;
            }

            .pushButton:focus {
                background-color: #873df2;
                color: white;
            }

            .pushButton:hover {
                background-color: #6e14ef;
                color: white;
            }

            .pushButton:pressed {
                background-color: #9452f3;
                color: white;
            }

            .pushButton:disabled {
                background-color: #cccccc;
                color: #838383;
            }
        """
        self.setStyleSheet(self.styles)

        # Connect the style updates to the changes of internal state.
        self.state.resting.entered.connect(lambda: self.setStyles(self.StateEnabled))
        self.state.disabled.entered.connect(lambda: self.setStyles(self.StateDisabled))
        self.state.hoverFromResting.entered.connect(lambda: self.setStyles(self.StateHover))
        self.state.hoverFromFocusFromResting.entered.connect(lambda: self.setStyles(self.StateHover))
        self.state.focusFromResting.entered.connect(lambda: self.setStyles(self.StateFocus))
        self.state.pressedFromHoverFromResting.entered.connect(lambda: self.setStyles(self.StatePressed))
        self.state.pressedFromFocusFromResting.entered.connect(lambda: self.setStyles(self.StatePressed))
        self.state.pressedFromHoverFromFocusFromResting.entered.connect(lambda: self.setStyles(self.StatePressed))

    def disable(self) -> None:
        """Disable the button."""
        self.state.disable()
        super().setDisabled(True)

    def enable(self) -> None:
        """Enable the button."""
        self.state.enable()
        super().setDisabled(False)

    def setDebug(self, debug: bool) -> None:
        """Set debug to replace the button text by its current state."""
        self.debug = debug

    def setStyles(self, state: State) -> None:
        """Set styles corresponding to a given button state.

        These visual effects follows the Material Design 2 guidelines for buttons.
        See https://material.io/components/buttons.html#contained-button

        The method contains some 'magic values' that are referred to in
        the widget's stylesheet. None of them needs to be used or modified
        by end-users.
        """
        if state is self.StateEnabled:
            self.setElevation(self.ElevationLow)
            self.setCursor(QCursor(Qt.PointingHandCursor))
            self.setStyleSheet(self.styles)
            if self.debug:
              self.setText("ENABLED")
        elif state is self.StateHover:
            self.setElevation(self.ElevationMedium)
            self.setStyleSheet(self.styles)
            if self.debug:
                self.setText("HOVER")
        elif state is self.StateFocus:
            self.setElevation(self.ElevationLow)
            self.setStyleSheet(self.styles)
            if self.debug:
                self.setText("FOCUSED")
        elif state is self.StatePressed:
            self.setElevation(self.ElevationHigh)
            self.setStyleSheet(self.styles)
            if self.debug:
                self.setText("PRESSED")
        else:
            self.setElevation(self.ElevationNone)
            self.setCursor(QCursor(Qt.ArrowCursor))
            self.setStyleSheet(self.styles)
            if self.debug:
                self.setText("DISABLED")

    def setElevation(self, value: Elevation) -> None:
        """
        Set a drop shadow to suggest widget elevation.

        This visual effect follows the Material Design 2 guidelines for buttons.
        See https://material.io/components/buttons.html#contained-button

        The method contains some 'magic values' that control the appearance
        of the shadow, based on the requested elevation. None of those needs
        to be used or modified by end-users, not even the elevation constants
        that are provided by this class.
        """
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(0, 1.5*value)
        shadow.setBlurRadius(4*value)
        shadow.setColor(QColor("#44000000"))
        self.setGraphicsEffect(shadow)
        self.update()
        
    def event(self, e: QEvent) -> bool:
        if type(e) is QHoverEvent:
            if e.oldPos() == QPoint(-1, -1):
                self.state.postEvent(e)
            if e.pos() == QPoint(-1, -1):
                self.state.postEvent(e)
        if type(e) is QFocusEvent:
            if e.gotFocus():
                self.state.postEvent(e)
            if e.lostFocus():
                self.state.postEvent(e)
        return super().event(e)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.key() == Qt.Key_Space:
            self.state.postEvent(e)
            self.state.press()  # Should not necessary. Bug workaround.
        return super().keyPressEvent(e)

    def keyReleaseEvent(self, e: QKeyEvent) -> None:
        if e.key() == Qt.Key_Space:
            self.state.postEvent(e)
        return super().keyReleaseEvent(e)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.LeftButton:
            self.state.postEvent(e)
        return super().mousePressEvent(e)

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        self.state.postEvent(e)
        return super().mouseReleaseEvent(e)

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
        disable.clicked.connect(lambda: button.disable())
        enable.clicked.connect(lambda: button.enable())

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
