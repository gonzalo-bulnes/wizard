import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from device import Device


class InsertDevicePage(QWizardPage):
    
    def __init__(self, device_state_changed: pyqtSignal, parent=None):
        super().__init__(parent)

        self.setTitle("Insert USB device")

        instructions = QLabel("The USB device must be encrypted with LUKS or Veracrypt.")
        instructions.setWordWrap(True)
        completion_message = QLabel("USB device found, feel free to change it if needed.")
        completion_message.hide()

        layout = QVBoxLayout()
        layout.addWidget(instructions)
        layout.addWidget(completion_message)
        self.setLayout(layout)

        device_state_changed.connect(self.completeChanged)
        self.completeChanged.connect(self._on_complete_changed)

        self.instructions = instructions
        self.completion_message = completion_message

    def _on_complete_changed(self) -> None:
        dirname = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(dirname, "page.css"), "r") as stylesheet:
            self.setStyleSheet(stylesheet.read())

    def isComplete(self) -> bool:
        device_state = self.wizard()._device.state
        is_complete = device_state == Device.LockedState or device_state == Device.UnlockedState or device_state == Device.UnlockingState

        if is_complete:
            self.instructions.hide()
            self.completion_message.show()
        else:
            self.instructions.show()
            self.completion_message.hide()

        return is_complete
