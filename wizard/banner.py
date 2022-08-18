from typing import NewType

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from state_transitions import SpecificKeyEventTransition, SpecificMouseButtonEventTransition
from dialog import Dialog


class DeviceState(QWidget):
    """The state of an export device (typically a USB device).

    There should be no need for you to use this class directly.

    Paste the following state chart in https://mermaid.live for
    a visual representation of the behavior implemented by this class!

    stateDiagram-v2
        DeviceNeverAvailable --> DeviceAvailable: device_verification_succeeded (system)
        DeviceAvailable --> DeviceWasAvailable: device_presence_verification_failed (system)
        DeviceAvailable --> DeviceWasAvailable: device_encryption_verification_failed (system)
        DeviceWasAvailable --> DeviceAvailable: device_verification_succeeded (system)
    """

    became_available = pyqtSignal()
    became_unavailable = pyqtSignal()

    def __init__(self, availability_signals: List(QSignal), unavailability_signals: List[QSignal]) -> None:
        super().__init__()

        for signal in availability_signals:
            signal.connect(self.became_available)

        for signal in unavailability_signals:
            signal.connect(self.became_unavailable)

        # Declare the state chart described in the docstring.
        # See https://doc.qt.io/qt-5/statemachine-api.html
        #
        # This is a very declarative exercise.
        # The state names are part of the API of this class.
        self._machine = QStateMachine()

        self.device_was_never_available = QState()
        self.device_recently_available = QState()
        self.device_currently_available = QState()

        self.device_was_never_available.addTransition(self, "became_available").addTargetState(self.device_currently_available)
        self.device_currently_available.addTransition(self, "became_unavailable").addTargetState(self.device_recently_available)
        self.device_recently_available.addTransition(self, "became_available").addTargetState(self.device_currently_available)

        self._machine.start()


class Banner(QWidget):
    """ A banner."""

    # These banner types are part of the Python API of this class,
    # and the string values are part of its QSS API.
    Type = NewType("Type", str)
    TypeSuccess = Type("success")
    TypeAlert = Type("alert")
    TypeInfo = Type("info")

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

        self.state = BannerState(self)
        self.device = Device()

        with open("banner.css", "r") as stylesheet:
            self.setStyleSheet(stylesheet.read())

        # Connect the style updates to the changes of internal state.
        #self.state.resting.entered.connect(lambda: self.setStyles(self.StateEnabled))
        #if self.debug:
        #    self.state.resting.entered.connect(lambda: print("resting"))
        #self.state.disabled.entered.connect(lambda: self.setStyles(self.StateDisabled))
        #if self.debug:
        #    self.state.disabled.entered.connect(lambda: print("disabled"))
        #self.state.hoverFromResting.entered.connect(lambda: self.setStyles(self.StateHover))
        #if self.debug:
        #    self.state.hoverFromResting.entered.connect(lambda: print("hoverFromResting"))
        #self.state.hoverFromFocusFromResting.entered.connect(lambda: self.setStyles(self.StateHover))
        #if self.debug:
        #    self.state.hoverFromFocusFromResting.entered.connect(lambda: print("hoverFromFocusFromResting"))
        #self.state.focusFromResting.entered.connect(lambda: self.setStyles(self.StateFocus))
        #if self.debug:
        #    self.state.focusFromResting.entered.connect(lambda: print("focusFromResting"))
        #self.state.pressedFromHoverFromResting.entered.connect(lambda: self.setStyles(self.StatePressed))
        #if self.debug:
        #    self.state.pressedFromHoverFromResting.entered.connect(lambda: print("pressedFromHoverFromResting"))
        #self.state.pressedFromFocusFromResting.entered.connect(lambda: self.setStyles(self.StatePressed))
        #if self.debug:
        #    self.state.pressedFromFocusFromResting.entered.connect(lambda: print("pressedFromFocusFromResting"))
        #self.state.pressedFromHoverFromFocusFromResting.entered.connect(lambda: self.setStyles(self.StatePressed))
        #if self.debug:
        #    self.state.pressedFromHoverFromFocusFromResting.entered.connect(lambda: print("pressedFromHoverFromFocusFromResting"))

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
