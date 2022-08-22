from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from device import Device


class Wizard(QWizard):

    # Private API to manage pages dynamically.
    device_missing: pyqtSignal()
    device_locked: pyqtSignal()
    device_unlocked: pyqtSignal()

    def __init__(self, device: Device, parent=None):
        super().__init__(parent)

        # Connect the device
        self._device = device
        self._device.state_changed.connect(self._on_device_state_changed)

        self.setWindowTitle("Wizard")
        self.setModal(False)
        self.setOptions(
            QWizard.NoBackButtonOnLastPage |
            QWizard.NoCancelButtonOnLastPage |
            QWizard.NoBackButtonOnStartPage
        )

        self._disclaimer_page = self._create_disclaimer_page()
        self._disclaimer_page_id = self.addPage(self._disclaimer_page)
        self._insert_device_page = self._create_insert_device_page(self._device.state_changed)
        self._insert_device_page_id = self.addPage(self._insert_device_page)
        self._unlock_device_page = self._create_unlock_device_page(self._device.state_changed, self._device.unlocking_failed)
        self._unlock_device_page_id = self.addPage(self._unlock_device_page)
        self._review_files_page = self._create_review_files_page()
        self._review_files_page_id = self.addPage(self._review_files_page)
        self._summary_page = self._create_summary_page()
        self._summary_page_id = self.addPage(self._summary_page)

        self.currentIdChanged.connect(self._on_page_changed)

    def _on_device_missing(self) -> None:
        current_page_id = self.currentId()
        if current_page_id > self._insert_device_page_id and current_page_id < self._summary_page_id:
            lastId = self.currentId()
            while self.currentId() != self._insert_device_page_id and self.currentId != lastId:
                lastId = self.currentId()
                self.back()

    def _on_device_locked(self) -> None:
        current_page_id = self.currentId()
        if current_page_id > self._unlock_device_page_id and current_page_id < self._summary_page_id:
            lastId = self.currentId()
            while self.currentId() != self._unlock_device_page_id and self.currentId != lastId:
                lastId = self.currentId()
                self.back()

    @pyqtSlot(str)
    def _on_device_state_changed(self, state: Device.State) -> None:
        device_state = self._device.state
        if device_state == Device.MissingState or device_state == Device.RemovedState:
            self._on_device_missing()
        elif device_state == Device.UnlockedState or device_state == Device.UnknownState:
            pass
        else:
            self._on_device_locked()

    @pyqtSlot(int)
    def _on_page_changed(self, id: int) -> None:
        self._on_device_state_changed(self._device.state)
        self._unlock_device_page.failure_message.hide()  # Hack, or at least overreach.

    def _create_disclaimer_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle("Disclaimer")

        content = QLabel("Please be aware that exporting files carries some <b>risks</b>.")
        content.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(content)
        page.setLayout(layout)

        return page

    def _create_insert_device_page(self, device_state_changed) -> QWizardPage:
        page = QWizardPage()
        page.setTitle("Insert USB device")

        instructions = QLabel("The USB device must be encrypted with LUKS or Veracrypt.")
        instructions.setWordWrap(True)
        completion_message = QLabel("USB device found, feel free to change it if needed.")
        completion_message.hide()

        layout = QVBoxLayout()
        layout.addWidget(instructions)
        layout.addWidget(completion_message)
        page.setLayout(layout)

        def _devicePageIsComplete() -> bool:
            is_complete = self._device.state == Device.LockedState or self._device.state == Device.UnlockedState

            if is_complete:
                instructions.hide()
                completion_message.show()
            else:
                instructions.show()
                completion_message.hide()

            return is_complete

        page.isComplete = _devicePageIsComplete
        device_state_changed.connect(page.completeChanged)

        return page

    def _create_review_files_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle("Review file list")

        content = QLabel("The following files will be exported: ...")
        content.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(content)
        page.setLayout(layout)

        return page

    def _create_unlock_device_page(self, device_state_changed, device_unlocking_failed) -> QWizardPage:
        page = QWizardPage()
        page.setTitle("Unlock USB device")

        label = QLabel("&Passphrase:")
        input = QLineEdit()
        label.setBuddy(input)
        completion_message = QLabel("USB device unlocked.")
        completion_message.hide()

        unlocking_message = QLabel("Unlocking USB device...")
        unlocking_message.hide()
        failure_message = QLabel("Failed to unlock the USB drive. Please verufy that the USB drive is adequately encrypted and the passphrase is correct.")
        failure_message.setWordWrap(True)
        failure_message.hide()
        page.failure_message = failure_message

        button = QPushButton("Unlock")

        layout = QVBoxLayout()
        layout.addWidget(failure_message)
        layout.addWidget(label)
        layout.addWidget(input)
        layout.addWidget(button)
        layout.addWidget(unlocking_message)
        layout.addWidget(completion_message)
        page.setLayout(layout)

        def _start_unlocking():
            passphrase = input.text()
            self._device.unlocking_started.emit(passphrase)

            label.hide()
            input.hide()
            button.hide()
            unlocking_message.show()
            failure_message.hide()

        button.clicked.connect(_start_unlocking)

        def _on_unlocking_failure():
            failure_message.show()

        device_unlocking_failed.connect(_on_unlocking_failure)

        def _exportPageIsComplete() -> bool:  # validate, not complete. Complete should go to unlocking state.
            is_complete = self._device.state == Device.UnlockedState

            if is_complete:
                label.hide()
                input.hide()
                button.hide()
                unlocking_message.hide()
                failure_message.hide()
                completion_message.show()
            else:
                label.show()
                input.show()
                button.show()
                unlocking_message.hide()
                completion_message.hide()

            return is_complete

        page.isComplete = _exportPageIsComplete
        device_state_changed.connect(page.completeChanged)

        def _next() -> None:
            self._device.attempt_unlocking()
            page.super().next()

        page.next = _next

        return page

    def _create_summary_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle("Done!")

        content = QLabel("Your files were exported successfully.")
        content.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(content)
        page.setLayout(layout)

        return page
