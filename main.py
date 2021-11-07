import sys
from typing import NewType

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# Magic values.
SEPARATOR = "separator"


class SpecificKeyEventTransition(QEventTransition):
    """A transition that triggers only on a QKeyEvent for a specific key (e.g. Qt.Key_Space)."""
    def __init__(self, object: QObject, type: QEvent.Type, key: int, sourceState: QState = None):
        super().__init__(object, type, sourceState)
        self._key = key

    def eventTest(self, event: QEvent) -> bool:
        if super().eventTest(event):
            we: QStateMachine.WrappedEvent = event
            return we.event().key() == self._key
        return False


class SpecificMouseButtonEventTransition(QEventTransition):
    """A transition that triggers only on a QMouseEvent for a specific button (e.g. Qt.LeftButton)."""
    def __init__(self, object: QObject, type: QEvent.Type, button: int, sourceState: QState = None):
        super().__init__(object, type, sourceState)
        self._button = button

    def eventTest(self, event: QEvent) -> bool:
        if super().eventTest(event):
            we: QStateMachine.WrappedEvent = event
            return we.event().button() == self._button
        return False


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
      enabled --> disabled: EnabledChange
      disabled --> enabled: EnabledChange

      state enabled {
        resting --> hoverFromResting: HoverEnter
        hoverFromResting --> resting: HoverLeave

        hoverFromResting --> pressedFromHoverFromResting: MouseButtonPress
        pressedFromHoverFromResting --> hoverFromResting: MouseButtonRelease

        resting --> focusFromResting: FocusIn
        focusFromResting --> resting: FocusOut

        focusFromResting --> pressedFromFocusFromResting: KeyPress
        pressedFromFocusFromResting --> focusFromResting: KeyRelease

        focusFromResting --> hoverFromFocusFromResting: HoverEnter
        hoverFromFocusFromResting --> focusFromResting: HoverLeave

        hoverFromFocusFromResting --> hoverFromResting: FocusOut

        hoverFromFocusFromResting --> pressedFromHoverFromFocusFromResting: MouseButtonPress
        pressedFromHoverFromFocusFromResting --> hoverFromFocusFromResting: MouseButtonRelease

        hoverFromFocusFromResting --> pressedFromHoverFromFocusFromResting: KeyPress
        pressedFromHoverFromFocusFromResting --> hoverFromFocusFromResting: KeyRelease
      }
    """

    def __init__(self, button: "PushButton") -> None:
        super().__init__()

        self._button = button

        # Declare the state chart described in the docstring.
        # See https://doc.qt.io/qt-5/statemachine-api.html
        #
        # This is a very declarative exercise.
        # The state names are part of the API of this class.
        self._machine = QStateMachine()

        self.enabled = QState()
        self.disabled = QState()
        QEventTransition(self._button, QEvent.EnabledChange, self.enabled).setTargetState(self.disabled)
        QEventTransition(self._button, QEvent.EnabledChange, self.disabled).setTargetState(self.enabled)

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

        QEventTransition(self._button, QEvent.HoverEnter, self.resting).setTargetState(self.hoverFromResting)
        QEventTransition(self._button, QEvent.HoverLeave, self.hoverFromResting).setTargetState(self.resting)

        SpecificMouseButtonEventTransition(self._button, QEvent.MouseButtonPress, Qt.LeftButton, self.hoverFromResting).setTargetState(self.pressedFromHoverFromResting)
        QEventTransition(self._button, QEvent.MouseButtonRelease, self.pressedFromHoverFromResting).setTargetState(self.hoverFromResting)

        QEventTransition(self._button, QEvent.FocusIn, self.resting).setTargetState(self.focusFromResting)
        QEventTransition(self._button, QEvent.FocusOut, self.focusFromResting).setTargetState(self.resting)

        SpecificKeyEventTransition(self._button, QEvent.KeyPress, Qt.Key_Space, self.focusFromResting).setTargetState(self.pressedFromFocusFromResting)
        SpecificKeyEventTransition(self._button, QEvent.KeyRelease, Qt.Key_Space, self.pressedFromFocusFromResting).setTargetState(self.focusFromResting)

        QEventTransition(self._button, QEvent.HoverEnter, self.focusFromResting).setTargetState(self.hoverFromFocusFromResting)
        QEventTransition(self._button, QEvent.HoverLeave, self.hoverFromFocusFromResting).setTargetState(self.focusFromResting)

        QEventTransition(self._button, QEvent.FocusOut, self.hoverFromFocusFromResting).setTargetState(self.hoverFromResting)

        SpecificMouseButtonEventTransition(self._button, QEvent.MouseButtonPress, Qt.LeftButton, self.hoverFromFocusFromResting).setTargetState(self.pressedFromHoverFromFocusFromResting)
        QEventTransition(self._button, QEvent.MouseButtonRelease, self.pressedFromHoverFromFocusFromResting).setTargetState(self.hoverFromFocusFromResting)

        SpecificKeyEventTransition(self._button, QEvent.KeyPress, Qt.Key_Space,  self.hoverFromFocusFromResting).setTargetState(self.pressedFromHoverFromFocusFromResting)
        SpecificKeyEventTransition(self._button, QEvent.KeyRelease, Qt.Key_Space, self.pressedFromHoverFromFocusFromResting).setTargetState(self.hoverFromFocusFromResting)

        self._machine.start()


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
    # They are used to set styles that are not supported by QSS,
    # for example, the drop shadow that suggests the button's elevation.
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
        self.debug = True

        self.setProperty("class", "button contained")
        self.styles = """
            .button {
                border-radius: 6px;
                font: 500 18px 'Monsterrat';
                margin-bottom: 1em;
                outline: none;
                padding: .6em 1em;
            }

            .contained {
                background-color: #6000ee;
                border: none;
                color: #ffffff;
            }

            .contained:focus {
                background-color: #873df2;
                color: white;
            }

            .contained:hover {
                background-color: #6e14ef;
                color: white;
            }

            .contained:pressed {
                background-color: #9452f3;
                color: white;
            }

            .contained:disabled {
                background-color: #cccccc;
                color: #838383;
            }
        """
        self.setStyleSheet(self.styles)

        # Connect the style updates to the changes of internal state.
        self.state.resting.entered.connect(lambda: self.setStyles(self.StateEnabled))
        if self.debug:
            self.state.resting.entered.connect(lambda: print("resting"))
        self.state.disabled.entered.connect(lambda: self.setStyles(self.StateDisabled))
        if self.debug:
            self.state.disabled.entered.connect(lambda: print("disabled"))
        self.state.hoverFromResting.entered.connect(lambda: self.setStyles(self.StateHover))
        if self.debug:
            self.state.hoverFromResting.entered.connect(lambda: print("hoverFromResting"))
        self.state.hoverFromFocusFromResting.entered.connect(lambda: self.setStyles(self.StateHover))
        if self.debug:
            self.state.hoverFromFocusFromResting.entered.connect(lambda: print("hoverFromFocusFromResting"))
        self.state.focusFromResting.entered.connect(lambda: self.setStyles(self.StateFocus))
        if self.debug:
            self.state.focusFromResting.entered.connect(lambda: print("focusFromResting"))
        self.state.pressedFromHoverFromResting.entered.connect(lambda: self.setStyles(self.StatePressed))
        if self.debug:
            self.state.pressedFromHoverFromResting.entered.connect(lambda: print("pressedFromHoverFromResting"))
        self.state.pressedFromFocusFromResting.entered.connect(lambda: self.setStyles(self.StatePressed))
        if self.debug:
            self.state.pressedFromFocusFromResting.entered.connect(lambda: print("pressedFromFocusFromResting"))
        self.state.pressedFromHoverFromFocusFromResting.entered.connect(lambda: self.setStyles(self.StatePressed))
        if self.debug:
            self.state.pressedFromHoverFromFocusFromResting.entered.connect(lambda: print("pressedFromHoverFromFocusFromResting"))

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
