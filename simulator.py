import sys
from typing import List

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from push_button import PushButton
from device import Device

LOADING_TIME_IN_MS = 500

class Simulator(QWidget):
    """A USB device simulator"""
    def __init__(self, device: Device, parent=None):
        super().__init__(parent)

        self._device = device

        # Connect the device.
        self._device.not_found.connect(self._on_device_not_found)
        self._device.found_locked.connect(self._on_device_found_locked)
        self._device.found_unlocked.connect(self._on_device_found_unlocked)
        self._device.unlocking_started.connect(self._on_device_unlocking_started)
        self._device.unlocking_failed.connect(self._on_device_found_locked)
        self._device.unlocking_succeeded.connect(self._on_device_found_unlocked)
        self._device.locked.connect(self._on_device_found_locked)
        
        self.setupUI()

        self._initialize_device()

    def setupUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        title = QLabel("<h1>USB Device Simulator</h1>")
        layout.addWidget(title)
        status = QLabel("<p>Loading...</p>")
        status.setWordWrap(True)
        layout.addWidget(status)

        self._status = status

        insertLockedDevice, insertUnlockedDevice, lockDevice, unlockDevice, removeDevice, simulateUnlockingFailure, simulateUnlockingSuccess  = self._create_buttons()
        self._buttons = {}
        self._buttons["device missing"] = [insertLockedDevice, insertUnlockedDevice]
        self._buttons["device locked"] = [unlockDevice, removeDevice]
        self._buttons["device unlocked"] = [lockDevice, removeDevice]
        self._buttons["all"] = [insertLockedDevice, insertUnlockedDevice, unlockDevice, lockDevice, removeDevice]
        
        self.show()


    def _create_buttons(self) -> List[PushButton]:

        insertLockedDevice = PushButton(PushButton.TypeContained)
        insertLockedDevice.setText("INSERT LOCKED USB DRIVE")
        insertLockedDevice.clicked.connect(self._on_locked_device_inserted)
        self.layout().addWidget(insertLockedDevice)
        insertLockedDevice.setEnabled(False)
        insertLockedDevice.hide()

        insertUnlockedDevice = PushButton(PushButton.TypeContained)
        insertUnlockedDevice.setText("INSERT UNLOCKED USB DRIVE")
        insertUnlockedDevice.clicked.connect(self._on_unlocked_device_inserted)
        self.layout().addWidget(insertUnlockedDevice)
        insertUnlockedDevice.setEnabled(False)
        insertUnlockedDevice.hide()

        lockDevice = PushButton(PushButton.TypeContained)
        lockDevice.setText("LOCK USB DRIVE")
        lockDevice.clicked.connect(self._on_device_locked)
        self.layout().addWidget(lockDevice)
        lockDevice.setEnabled(False)
        lockDevice.hide()

        unlockDevice = PushButton(PushButton.TypeContained)
        unlockDevice.setText("UNLOCK USB DRIVE")
        unlockDevice.clicked.connect(self._on_device_unlocked)
        self.layout().addWidget(unlockDevice)
        unlockDevice.setEnabled(False)
        unlockDevice.hide()

        removeDevice = PushButton(PushButton.TypeContained)
        removeDevice.setText("REMOVE USB DRIVE")
        removeDevice.clicked.connect(self._on_device_removed)
        self.layout().addWidget(removeDevice)
        removeDevice.setEnabled(False)
        removeDevice.hide()

        simulateUnlockingSuccess = PushButton(PushButton.TypeContained)
        simulateUnlockingSuccess.setText("REMOVE USB DRIVE")
        simulateUnlockingSuccess.clicked.connect(self._on_device_unlocking_succeeded)
        self.layout().addWidget(simulateUnlockingSuccess)
        simulateUnlockingSuccess.setEnabled(False)
        simulateUnlockingSuccess.hide()

        simulateUnlockingFailure = PushButton(PushButton.TypeContained)
        simulateUnlockingFailure.setText("REMOVE USB DRIVE")
        simulateUnlockingFailure.clicked.connect(self._on_device_unlocking_failed)
        self.layout().addWidget(simulateUnlockingFailure)
        simulateUnlockingFailure.setEnabled(False)
        simulateUnlockingFailure.hide()

        return [insertLockedDevice, insertUnlockedDevice, lockDevice, unlockDevice, removeDevice, simulateUnlockingSuccess, simulateUnlockingFailure]


    def _initialize_device(self) -> None:
        timer = QTimer()
        timer.timeout.connect(lambda: self._device.check(Device.EmitNotFound))
        timer.timeout.connect(lambda: self._timer.stop())
        timer.start(LOADING_TIME_IN_MS)
        self._timer = timer

    def _on_device_not_found(self) -> None:
        self._status.setText("<b>No USB drive is present.</b>")
        for button in self._buttons["all"]:
            button.hide()
            button.setEnabled(False)
        for button in self._buttons["device missing"]:
            button.show()
            button.setEnabled(True)

    def _on_device_found_locked(self) -> None:
        self._status.setText("A <b>locked</b> USB drive is present.")
        for button in self._buttons["all"]:
            button.hide()
            button.setEnabled(False)
        for button in self._buttons["device locked"]:
            button.show()
            button.setEnabled(True)

    def _on_device_found_unlocked(self) -> None:
        self._status.setText("An <b>unlocked</b> USB drive is present.")
        for button in self._buttons["all"]:
            button.hide()
            button.setEnabled(False)
        for button in self._buttons["device unlocked"]:
            button.show()
            button.setEnabled(True)
        
    def _on_device_unlocking_started(self) -> None:
        self._status.setText("A <b>locked</b> USB drive is present. A passphrase was submitted to unlock theUSB drive.")
        for button in self._buttons["all"]:
            button.hide()
            button.setEnabled(False)
        for button in self._buttons["device unlocking"]:
            button.show()
            button.setEnabled(True)

    def _on_device_unlocking_succeeded(self) -> None:
        self._on_device_found_unlocked()

    def _on_device_unlocking_failed(self) -> None:
        self._on_device_found_locked()

    def _on_locked_device_inserted(self):
        self._device.check(Device.EmitFoundLocked)

    def _on_unlocked_device_inserted(self):
        self._device.check(Device.EmitFoundUnlocked)

    def _on_device_removed(self):
        self._device.check(Device.EmitNotFound)

    def _on_device_locked(self):
        self._device.check(Device.EmitLocked)

    def _on_device_unlocking_success_simulated(self):
        self._device.check(Device.EmitUnlockingSucceeded)

    def _on_device_unlocking_failure_simulated(self):
        self._device.check(Device.EmitUnlockingFailed)


    def _on_device_unlocked(self):
        self._device.check(Device.EmitUnlockingSucceeded)
