from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from device import Device

class Wizard(QWizard):
    def __init__(self, device: Device, parent=None):
        super().__init__(parent)

        self._device = device
        self._device.state_changed.connect(self._on_device_state_changed)

        self.setWindowTitle("Wizard")
        self.setModal(False)

        self.addPage(self._create_disclaimer_page())
        self._device_page_id = self.addPage(self._create_device_page())
        self._export_page_id = self.addPage(self._create_export_page())
        self.addPage(self._create_files_page())
        self._summary_page_id = self.addPage(self._create_summary_page())

        self.currentIdChanged.connect(self._on_page_changed)

    @pyqtSlot(str)
    def _on_device_state_changed(self, state: Device.State) -> None:
            # Device presence
            if self.currentId() == self._device_page_id:
                if self._device.state == Device.UnknownState or self._device.state == Device.MissingState or self._device.state == Device.RemovedState:
                    print("Blocking until a device is inserted.")
                    self.button(QWizard.NextButton).setEnabled(False)
                elif not self.button(QWizard.NextButton).isEnabled():
                    self.button(QWizard.NextButton).setEnabled(True)
                return
            else:
                if self._device.state == Device.RemovedState and self.currentId() > self._device_page_id and self.currentId() < self._summary_page_id:
                    print("Device must be inserted!")
                    lastId = self.currentId()
                    while self.currentId() != self._device_page_id and self.currentId != lastId:
                        lastId = self.currentId()
                        self.back()

                # Device locking status
                if self._device.state != Device.UnlockedState and self.currentId() > self._export_page_id and self.currentId() < self._summary_page_id:
                    print("Device must be unlocked!")
                    lastId = self.currentId()
                    while self.currentId() != self._export_page_id and self.currentId != lastId:
                        lastId = self.currentId()
                        self.back()


    @pyqtSlot(int)
    def _on_page_changed(self, id: int) -> None:
        if id == self._device_page_id:
            self._display_device_state()
        self._on_device_state_changed(self._device.state)

    def _display_device_state(self) -> None:
        print(f"The device state is currently: {self._device.state}")

    def _create_disclaimer_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle("Disclaimer")

        content = QLabel("Please be aware that exporting files carries some <b>risks</b>.")
        content.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(content)
        page.setLayout(layout)

        return page

    def _create_device_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle("Insert USB device")

        content = QLabel("The USB device must be encrypted with LUKS or Veracrypt.")
        content.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(content)
        page.setLayout(layout)

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

    def _create_export_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle("Unlock USB device")

        label = QLabel("Passphrase:")
        input = QLineEdit()

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(input)
        page.setLayout(layout)

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


class State(QObject):
    def __init__(self):
        super().__init__()
