from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from device import Device


class UnlockDevicePage(QWizardPage):
    
    def __init__(self, device_state_changed: pyqtSignal, device_unlocking_failed: pyqtSignal, parent=None):
        super().__init__(parent)
        self.setTitle("Unlock USB device")

        label = QLabel("&Passphrase:")
        input = QLineEdit()
        label.setBuddy(input)
        completion_message = QLabel("USB device unlocked.")
        completion_message.hide()

        unlocking_message = QLabel("Unlocking USB device...")
        unlocking_message.hide()
        failure_message = QLabel("Failed to unlock the USB drive. Please verify that it is adequately encrypted (LUKS or VeraCrypt) and the passphrase is correct.")
        failure_message.setWordWrap(True)
        failure_message.hide()

        button = QPushButton("Unlock")
        button.clicked.connect(self._start_unlocking)

        layout = QVBoxLayout()
        layout.addWidget(failure_message)
        layout.addWidget(label)
        layout.addWidget(input)
        layout.addWidget(button)
        layout.addWidget(unlocking_message)
        layout.addWidget(completion_message)
        self.setLayout(layout)

        device_unlocking_failed.connect(self._on_unlocking_failure)
        device_state_changed.connect(self.completeChanged)

        self.label = label
        self.input = input
        self.button = button
        self.completion_message = completion_message
        self.unlocking_message = unlocking_message
        self.failure_message = failure_message

    @pyqtSlot()
    def _start_unlocking(self):
        passphrase = self.input.text()
        self.wizard()._device.unlocking_started.emit(passphrase)

        self.label.hide()
        self.input.hide()
        self.button.hide()
        self.unlocking_message.show()
        self.failure_message.hide()

    @pyqtSlot()
    def _on_unlocking_failure(self):
        self.failure_message.show()

    def isComplete(self) -> bool:
        is_complete = self.wizard()._device.state == Device.UnlockedState

        if is_complete:
            self.label.hide()
            self.input.hide()
            self.button.hide()
            self.unlocking_message.hide()
            self.failure_message.hide()
            self.completion_message.show()
        else:
            self.label.show()
            self.input.show()
            self.button.show()
            self.unlocking_message.hide()
            self.completion_message.hide()

        return is_complete
