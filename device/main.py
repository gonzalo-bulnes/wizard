from typing import NewType

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class _State(QWidget):
    """
    Paste the following state chart in https://mermaid.live for
    a visual representation of the behavior implemented by this class!

    stateDiagram-v2
      [*] --> unknown
      unknown --> unlocked: found_unlocked
      unknown --> locked: found_locked
      unknown --> missing: not_found

      missing --> unlocked: found_unlocked
      missing --> locked: found_locked

      locked --> missing: not_found
      unlocked --> missing: not_found

      state locked {
        [*] --> resting
        resting --> unlocking: unlocking_started
        unlocking --> resting: unlocking_failed
      }

      locked --> unlocked: unlocking_succeeded
      unlocked --> locked: locked
    """
    def __init__(self, device: "Device"):
        super().__init__()

        self._device = device

        # Declare the state chart described in the docstring.
        # See https://doc.qt.io/qt-5/statemachine-api.html
        #
        # This is a very declarative exercise.
        # The state names are part of the API of this class.
        self._machine = QStateMachine()

        self.unknown = QState()
        self.missing = QState()
        self.locked = QState()
        self.unlocked = QState()

        self.unknown.addTransition(self._device.found_unlocked, self.unlocked)
        self.unknown.addTransition(self._device.found_locked, self.locked)
        self.unknown.addTransition(self._device.not_found, self.missing)

        self.missing.addTransition(self._device.found_unlocked, self.unlocked)
        self.missing.addTransition(self._device.found_locked, self.locked)

        self.locked.addTransition(self._device.not_found, self.missing)
        self.unlocked.addTransition(self._device.not_found, self.missing)

        self.resting = QState(self.locked)
        self.unlocking = QState(self.locked)

        self.locked.setInitialState(self.resting)
        self.resting.addTransition(self._device.unlocking_started, self.unlocking)
        self.unlocking.addTransition(self._device.unlocking_failed, self.resting)

        self.locked.addTransition(self._device.unlocking_succeeded, self.unlocked)
        self.unlocked.addTransition(self._device.locked, self.locked)

        self._machine.addState(self.unknown)
        self._machine.addState(self.missing)
        self._machine.addState(self.locked)
        self._machine.addState(self.unlocked)
        self._machine.setInitialState(self.unknown)

        self._machine.start()


class Device(QObject):

    # These signals are part of the device private API.
    # They are used internally to keep track of the device state by
    # triggering state machine transitions in the _State instance.
    #
    # In this demo, the simulator connects to this API, but that's a hack.
    found_locked = pyqtSignal()
    found_unlocked = pyqtSignal()
    not_found = pyqtSignal()
    unlocking_succeeded = pyqtSignal()
    unlocking_failed = pyqtSignal()
    locked = pyqtSignal()
    # Additionally, unlocking_started (below) is used too.

    # These two signals and states are part of the device public API,
    # along with the public methods.
    state_changed = pyqtSignal(str)
    unlocking_started = pyqtSignal(str)

    State = NewType("State", str)
    UnknownState = State("unknown")
    MissingState = State("missing")
    LockedState = State("locked")
    UnlockingState = State("unlocking")
    UnlockedState = State("unlocked")
    RemovedState = State("removed")


    def __init__(self):
        super().__init__()

        self._state = _State(self)

        # Track changes of state for public consumption.
        self._state.unknown.entered.connect(self._on_unknown_state_entered)
        self._state.missing.entered.connect(self._on_missing_state_entered)
        self._state.unlocking.entered.connect(self._on_unlocking_state_entered)
        self._state.resting.entered.connect(self._on_locked_state_entered)
        self._state.unlocked.entered.connect(self._on_unlocked_state_entered)

    @property
    def state(self) -> "Device.State":
        return self._current_state

    def emit_state_changed(func):
        def decorated(self):
            func(self)
            self.state_changed.emit(self._current_state)
        return decorated

    def attempt_unlocking(self, passphrase: str) -> None:
        self.unlocking_started.emit(passphrase)

    @emit_state_changed
    def _on_missing_state_entered(self) -> None:
        if self.state == Device.UnknownState:
            self._current_state = Device.MissingState
        else:
            # We can get subtle because we have access
            # to two subsequent states.
            # Some user interfaces could take advantage
            # of distinctions like this one.
            self._current_state = Device.RemovedState

    @emit_state_changed
    def _on_unlocking_state_entered(self) -> None:
        self._current_state = Device.UnlockingState

    @emit_state_changed
    def _on_locked_state_entered(self) -> None:
        self._current_state = Device.LockedState

    @emit_state_changed
    def _on_unlocked_state_entered(self) -> None:
        self._current_state = Device.UnlockedState

    @emit_state_changed
    def _on_unknown_state_entered(self) -> None:
        self._current_state = Device.UnknownState

    # These commands and method are specific to the demonstration code,
    # they wouldn't be present if it wasn't for the simulator.
    #
    # If this class depended in some service responsible for monitoring
    # the actual state of the device outside of the GUI, a similar API
    # could be defined to bring the information into the GUI scope.

    Command = NewType("Command", str)
    EmitFoundLocked = Command("found_locked")
    EmitFoundUnlocked = Command("found_unlocked")
    EmitNotFound = Command("not_found")
    EmitUnlockingSucceeded = Command("unlocking_succeeded")
    EmitUnlockingFailed = Command("unlocking_failed")
    EmitLocked = Command("locked")

    def check(self, desired_result: Command) -> None:
        """This method is specific to the demonstration code."""
        #print("Simulating a device check...")
        if desired_result == Device.EmitFoundLocked:
            self.found_locked.emit()
            #print("Locked device found.")
        if desired_result == Device.EmitFoundUnlocked:
            self.found_unlocked.emit()
            #print("Unlocked device found.")
        if desired_result == Device.EmitNotFound:
            #print("Device not found.")
            self.not_found.emit()
        if desired_result == Device.EmitUnlockingSucceeded:
            #print("Device successfully unlocked.")
            self.unlocking_succeeded.emit()
        if desired_result == Device.EmitUnlockingFailed:
            #print("Device unlocking failed.")
            self.unlocking_failed.emit()
        if desired_result == Device.EmitLocked:
            #print("Device locked.")
            self.locked.emit()
