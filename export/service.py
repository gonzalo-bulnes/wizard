from typing import NewType

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from device import Device

class Service(QObject):

    # These signals are part of the service public API.
    failed = pyqtSignal()
    succeeded = pyqtSignal()
    started = pyqtSignal()
    finished = pyqtSignal()

    # These commands are specific to the demonstration code.
    Command = NewType("Command", str)
    EmitFailed = Command("failed")
    EmitSucceeded = Command("succeeded")
    EmitFinished = Command("finished")

    def __init__(self, device: Device):
        super().__init__()

        self._device = device

        # Ensure that changed in the device state affect the exports.
        # TODO

    @pyqtSlot()
    def start(self):
        self.started.emit()

    def check(self, result: Command) -> None:
        """This method is specific to the demonstration code."""
        #print("Simulating a device check...")
        if result == Service.EmitFailed:
            self.failed.emit()
            self.finished.emit()
            #print("Export failed.")
        if result == Service.EmitSucceeded:
            self.succeeded.emit()
            self.finished.emit()
            #print("Export suceeded")
        if result == Service.EmitFinished:
            self.finished.emit()
            #print("Export finished")
