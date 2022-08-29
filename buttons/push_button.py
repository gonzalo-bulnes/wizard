import os
from typing import NewType

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .state_transitions import SpecificKeyEventTransition, SpecificMouseButtonEventTransition


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
        [*] --> resting
        resting --> hoverFromResting: HoverEnter
        hoverFromResting --> resting: HoverLeave

        hoverFromResting --> pressedFromHoverFromResting: MouseButtonPress
        pressedFromHoverFromResting --> hoverFromFocusFromResting: MouseButtonRelease

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
        QEventTransition(self._button, QEvent.MouseButtonRelease, self.pressedFromHoverFromResting).setTargetState(self.hoverFromFocusFromResting)

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

    def start(self, initially_enabled: bool = True) -> None:
        self._machine.setInitialState(self.enabled)
        if not initially_enabled:
            self._machine.setInitialState(self.disabled)
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

    # These button types are part of the Python API of this class,
    # and the string values are part of its QSS API.
    Type = NewType("Type", str)
    TypeContained = Type("contained")
    TypeOutlined = Type("outlined")
    TypeText = Type("text")

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

    def __init__(self, type: Type = TypeContained, parent=None):
        super().__init__(parent)

        self.state = PushButtonState(self)
        self.type = type
        self.debug = False

        self.setClasses(type)

        dirname = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(dirname, "push_button.css"), "r") as stylesheet:
            self.setStyleSheet(stylesheet.read())

        self._start_state_machine()

    def _start_state_machine(self) -> None:
        """Ensures that the initial state is correct.

        The button instance must be created before setEnabled() is called,
        at which point its inital state becomes known.
        The state machine must be started before its state transitions are acted upon.
        """
        QTimer.singleShot(200, lambda: self.state.start(self.isEnabled()))
        QTimer.singleShot(200, lambda: self._connect_state_transitions())

    def _connect_state_transitions(self) -> None:
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

    def setClasses(self, type: Type) -> None:
        """Set QSS class for styling purposes."""
        self.setProperty("class", f"button {type}")

    def setDebug(self, debug: bool) -> None:
        """Set debug to replace the button text by its current state."""
        self.debug = debug

    def setStyles(self, state: State) -> None:
        """Set styles corresponding to a given button state that are not supported by QSS.

        These visual effects follows the Material Design 2 guidelines for buttons.
        See https://material.io/components/buttons.html#contained-button
        """
        if state is self.StateEnabled:
            self.setCursor(QCursor(Qt.PointingHandCursor))
            if self.type is self.TypeContained:
                self.setElevation(self.ElevationLow)
            if self.debug:
              self.setText("ENABLED")
        elif state is self.StateHover:
            if self.type is self.TypeContained:
                self.setElevation(self.ElevationMedium)
            if self.debug:
                self.setText("HOVER")
        elif state is self.StateFocus:
            if self.type is self.TypeContained:
                self.setElevation(self.ElevationLow)
            if self.debug:
                self.setText("FOCUSED")
        elif state is self.StatePressed:
            if self.type is self.TypeContained:
                self.setElevation(self.ElevationHigh)
            if self.debug:
                self.setText("PRESSED")
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))
            if self.type is self.TypeContained:
                self.setElevation(self.ElevationNone)
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
        shadow.setOffset(0, 1*value)
        shadow.setBlurRadius(3*value)
        shadow.setColor(QColor("#44000000"))
        self.setGraphicsEffect(shadow)
        self.update()
