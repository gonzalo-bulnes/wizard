from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from device import Device

class PassphraseInput(QWidget):

    button_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        label = QLabel("&Passphrase:")
        input = QLineEdit()
        label.setBuddy(input)

        button = QPushButton("Unlock")
        button.clicked.connect(self.button_clicked)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(input)
        layout.addWidget(button)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        self.input = input

    def text(self) -> str:
        return self.input.text()


class UnlockDevicePage(QWizardPage):
    
    def __init__(self, device_state_changed: pyqtSignal, device_unlocking_failed: pyqtSignal, parent=None):
        super().__init__(parent)
        self.setTitle("Unlock USB device")

        passphrase_input = PassphraseInput()
        completion_message = QLabel("USB device unlocked.")
        completion_message.hide()

        unlocking_message = QLabel("Unlocking USB device...")
        unlocking_message.hide()
        failure_message = QLabel("Failed to unlock the USB drive. Please verify that it is adequately encrypted (LUKS or VeraCrypt) and the passphrase is correct.")
        failure_message.setWordWrap(True)
        failure_message.hide()

        passphrase_input.button_clicked.connect(self._start_unlocking)

        layout = QVBoxLayout()
        layout.addWidget(failure_message)
        layout.addWidget(passphrase_input)
        layout.addWidget(unlocking_message)
        layout.addWidget(completion_message)
        self.setLayout(layout)

        device_unlocking_failed.connect(self._on_unlocking_failure)
        device_state_changed.connect(self.completeChanged)

        self.passphrase_input = passphrase_input
        self.completion_message = completion_message
        self.unlocking_message = unlocking_message
        self.failure_message = failure_message

    @pyqtSlot()
    def _start_unlocking(self):
        passphrase = self.passphrase_input.text()
        self.wizard()._device.unlocking_started.emit(passphrase)

        self.passphrase_input.hide()
        self.unlocking_message.show()
        self.failure_message.hide()

    @pyqtSlot()
    def _on_unlocking_failure(self):
        self.failure_message.show()

    def isComplete(self) -> bool:
        device_state = self.wizard()._device.state
        is_complete = device_state == Device.UnlockedState

        if is_complete:
            self.passphrase_input.hide()
            self.unlocking_message.hide()
            self.failure_message.hide()
            self.completion_message.show()
        else:
            self.passphrase_input.show()
            self.unlocking_message.hide()
            self.completion_message.hide()

        return is_complete
