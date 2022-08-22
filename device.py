from typing import NewType

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class State(QWidget):
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
    # They are used to keep track of the device state.

    found_locked = pyqtSignal()
    found_unlocked = pyqtSignal()
    not_found = pyqtSignal()

    unlocking_started = pyqtSignal(str)
    unlocking_succeeded = pyqtSignal()
    unlocking_failed = pyqtSignal()

    locked = pyqtSignal()

    # These commands are specific to the demonstration code.
    Command = NewType("Command", str)
    EmitFoundLocked = Command("found_locked")
    EmitFoundUnlocked = Command("found_unlocked")
    EmitNotFound = Command("not_found")
    EmitUnlockingSucceeded = Command("unlocking_succeeded")
    EmitUnlockingFailed = Command("unlocking_failed")
    EmitLocked = Command("locked")

    # These states are private.
    State = NewType("State", str)
    UnknownState = State("unknown")
    MissingState = State("missing")
    LockedState = State("locked")
    UnlockingState = State("unlocking")
    UnlockedState = State("unlocked")
    RemovedState = State("removed")

    # These signals are part of the device public API.
    is_missing = pyqtSignal()
    inserted_locked = pyqtSignal()
    inserted_unlocked = pyqtSignal()
    unlocking_has_started = pyqtSignal()
    unlocking_has_succeeded = pyqtSignal()
    unlocking_has_failed = pyqtSignal()
    removed = pyqtSignal()

    state_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self._state = State(self)

        # Make the changes of state public:
        self._state.missing.entered.connect(self._on_missing_state_entered)
        self._state.unlocking.entered.connect(self._on_unlocking_state_entered)
        self._state.resting.entered.connect(self._on_locked_state_entered)
        self._state.unlocked.entered.connect(self._on_unlocked_state_entered)

        self._current_state = Device.UnknownState

    @property
    def state(self):
        return self._current_state

    @state.setter
    def state(self, state: "Device.State"):
        #print(f"Updated state to {state}")
        self._current_state = state
        self.state_changed.emit(state)

    def _on_missing_state_entered(self) -> None:
        if self.state == Device.UnknownState:
            self.state = Device.MissingState
            self.is_missing.emit()
        else:
            self.state = Device.RemovedState
            self.removed.emit()

    def _on_unlocking_state_entered(self) -> None:
        self.state = Device.UnlockingState
        self.unlocking_has_started.emit()

    def _on_locked_state_entered(self) -> None:
        if self.state == Device.UnlockingState:
            self.unlocking_has_failed.emit()
        else:
            self.inserted_locked.emit()
        self.state = Device.LockedState

    def _on_unlocked_state_entered(self) -> None:
        self.state = Device.UnlockedState
        self.unlocking_has_succeeded.emit()

    def attempt_unlocking(self):
        self.unlocking_started.emit()

    def check(self, result: Command) -> None:
        """This method is specific to the demonstration code."""
        #print("Simulating a device check...")
        if result == Device.EmitFoundLocked:
            self.found_locked.emit()
            #print("Locked device found.")
        if result == Device.EmitFoundUnlocked:
            self.found_unlocked.emit()
            #print("Unlocked device found.")
        if result == Device.EmitNotFound:
            #print("Device not found.")
            self.not_found.emit()
        if result == Device.EmitUnlockingSucceeded: 
            #print("Device successfully unlocked.")
            self.unlocking_succeeded.emit()
        if result == Device.EmitUnlockingFailed:
            #print("Device unlocking failed.")
            self.unlocking_failed.emit()
        if result == Device.EmitLocked:
            #print("Device locked.")
            self.locked.emit()
