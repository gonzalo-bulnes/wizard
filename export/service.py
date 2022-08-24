from typing import NewType

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from device import Device

class Service(QObject):

    # These signals are part of the service public API,
    # along with the public methods.
    failed = pyqtSignal()
    succeeded = pyqtSignal()
    started = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, device: Device):
        super().__init__()

        self._device = device

        self._device.state_changed.connect(self._on_device_state_changed)

        self.failed.connect(self.finished)
        self.succeeded.connect(self.finished)

    def start(self) -> None:
        self.started.emit()
        # ...and do whatever the export is supposed to be.
        #
        # This method would require proper error handling,
        # and probably some guards along the lines of:
        # if self._device.state != Device.UnlockedState:

    def _on_device_state_changed(self, state: Device.State) -> None:
        if state != Device.UnlockedState:
            self.failed.emit()

    # These commands and method are specific to the demonstration code.
    Command = NewType("Command", str)
    EmitFailed = Command("failed")
    EmitSucceeded = Command("succeeded")
    EmitFinished = Command("finished")

    def check(self, desired_result: Command) -> None:
        """This method is specific to the demonstration code."""
        #print("Simulating a device check...")
        if desired_result == Service.EmitFailed:
            self.failed.emit()
            #print("Export failed.")
        if desired_result == Service.EmitSucceeded:
            self.succeeded.emit()
            #print("Export suceeded")
        if desired_result == Service.EmitFinished:
            self.finished.emit()
            #print("Export finished")
