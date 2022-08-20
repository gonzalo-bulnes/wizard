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

        self._disclaimer_page = self._create_disclaimer_page()
        self._disclaimer_page_id = self.addPage(self._disclaimer_page)
        self._device_page = self._create_device_page(self._device.state_changed)
        self._device_page_id = self.addPage(self._device_page)
        self._export_page = self._create_export_page(self._device.state_changed)
        self._export_page_id = self.addPage(self._export_page)
        self._files_page = self._create_files_page()
        self._files_page_id = self.addPage(self._files_page)
        self._summary_page = self._create_summary_page()
        self._summary_page_id = self.addPage(self._summary_page)

        self.currentIdChanged.connect(self._on_page_changed)

    def _on_device_missing(self) -> None:
        current_page_id = self.currentId()
        if current_page_id > self._device_page_id and current_page_id < self._summary_page_id:
                #print("Device must be inserted!")
                #self.setPage(self._device_page_id, self._device_page)  # could memoize this
                #self.initializePage(current_page_id)
                lastId = self.currentId()
                while self.currentId() != self._device_page_id and self.currentId != lastId:
                    lastId = self.currentId()
                    self.back()

    def _on_device_locked(self) -> None:
        current_page_id = self.currentId()
        if current_page_id > self._export_page_id and current_page_id < self._summary_page_id:
            #print("Device must be unlocked!")
            #self.setPage(self._export_page_id, self._export_page)  # could memoize this
            #self.initializePage(current_page_id)
            lastId = self.currentId()
            while self.currentId() != self._export_page_id and self.currentId != lastId:
                lastId = self.currentId()
                self.back()

    def _on_device_unlocked(self) -> None:
        #print("_on_device_unlocked")
        current_page_id = self.currentId()
        if current_page_id != self._export_page_id:
            #print("No need to prompt for a passphrase")
            #self.removePage(self._export_page_id)
            #self.initializePage(current_page_id)
            pass

    def _on_device_inserted(self) -> None:
        current_page_id = self.currentId()
        if current_page_id != self._device_page_id:
            #print("No need to prompt for a device to be inserted")
            #self.removePage(self._device_page_id)
            #self.initializePage(current_page_id)
            pass
        

    @pyqtSlot(str)
    def _on_device_state_changed(self, state: Device.State) -> None:
        device_state = self._device.state
        if device_state == Device.MissingState or device_state == Device.RemovedState:
            self._on_device_missing()
        elif device_state == Device.UnlockedState:
            self._on_device_inserted()
            self._on_device_unlocked()
        elif device_state == Device.UnknownState:
            pass
        else:
            self._on_device_inserted()
            self._on_device_locked()

    @pyqtSlot(int)
    def _on_page_changed(self, id: int) -> None:
        #if id == self._device_page_id:
        #    self._display_device_state()
        self._on_device_state_changed(self._device.state)

    #def _display_device_state(self) -> None:
    #    print(f"The device state is currently: {self._device.state}")

    def _create_disclaimer_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle("Disclaimer")

        content = QLabel("Please be aware that exporting files carries some <b>risks</b>.")
        content.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(content)
        page.setLayout(layout)

        return page

    def _create_device_page(self, device_state_changed) -> QWizardPage:
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

    def _create_files_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle("Review file list")

        content = QLabel("The following files will be exported: ...")
        content.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(content)
        page.setLayout(layout)

        return page

    def _create_export_page(self, device_state_changed) -> QWizardPage:
        page = QWizardPage()
        page.setTitle("Unlock USB device")

        label = QLabel("Passphrase:")
        input = QLineEdit()
        completion_message = QLabel("USB device unlocked.")
        completion_message.hide()

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(input)
        layout.addWidget(completion_message)
        page.setLayout(layout)

        def _exportPageIsComplete() -> bool:
            is_complete = self._device.state == Device.UnlockedState

            if is_complete:
                label.hide()
                input.hide()
                completion_message.show()
            else:
                label.show()
                input.show()
                completion_message.hide()

            return is_complete

        page.isComplete = _exportPageIsComplete
        device_state_changed.connect(page.completeChanged)

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
