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

    _hoverInEventTriggered = pyqtSignal()
    _hoverOutEventTriggered = pyqtSignal()
    _focusInEventTriggered = pyqtSignal()
    _focusOutEventTriggered = pyqtSignal()
    _mousePressEventTriggered = pyqtSignal()
    _mouseReleaseEventTriggered = pyqtSignal()

    def __init__(self, button: QPushButton) -> None:
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

        self.resting.addTransition(self._hoverInEventTriggered, self.hoverFromResting)
        hoverEnterTransition = QEventTransition(self.button, QEvent.HoverEnter) 
        hoverEnterTransition.setTargetState(self.hoverFromResting)
        self.resting.addTransition(hoverEnterTransition)
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

    def enbable(self) -> None:
        self.enableActionTriggered.emit()

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

    def postEvent(self, e: QEvent) -> None:
        self._machine.postEvent(e)

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

        self.styles = f"""
            * {{
                border: none;
                border-radius: 6px;
                font: 500 18px 'Monsterrat';
                margin-bottom: 1em;
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

    def setStyles(self, state: State) -> None:
        """Set styles corresponding to a given button state.

        These visual effects follows the Material Design 2 guidelines for buttons.
        See https://material.io/components/buttons.html#contained-button

        The method contains some 'magic values' that are referred to in
        the widget's stylesheet. None of them needs to be used or modified
        by end-users.
        """
        if state is self.StateEnabled:
            self.setProperty("class", "enabled")
            self.setElevation(self.ElevationLow)
            self.setCursor(QCursor(Qt.PointingHandCursor))
            self.setStyleSheet(self.styles)
            if self.debug:
              self.setText("ENABLED")
        elif state is self.StateHover:
            self.setProperty("class", "hover")
            self.setElevation(self.ElevationMedium)
            self.setStyleSheet(self.styles)
            if self.debug:
                self.setText("HOVER")
        elif state is self.StateFocus:
            self.setProperty("class", "focus")
            self.setElevation(self.ElevationLow)
            self.setStyleSheet(self.styles)
            if self.debug:
                self.setText("FOCUSED")
        elif state is self.StatePressed:
            self.setProperty("class", "pressed")
            self.setElevation(self.ElevationHigh)
            self.setStyleSheet(self.styles)
            if self.debug:
                self.setText("PRESSED")
        else:
            self.setProperty("class", "disabled")
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
                #self.state.hoverIn()
                self.state.postEvent(e)
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
