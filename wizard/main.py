from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from device import Device
from .pages import StartPage, InsertDevicePage, UnlockDevicePage, ReviewDataPage, ExportPage


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

        self._disclaimer_page = StartPage()
        self._disclaimer_page_id = self.addPage(self._disclaimer_page)
        self._insert_device_page = InsertDevicePage(self._device.state_changed)
        self._insert_device_page_id = self.addPage(self._insert_device_page)
        self._unlock_device_page = UnlockDevicePage(self._device)
        self._unlock_device_page_id = self.addPage(self._unlock_device_page)
        self._review_files_page = ReviewDataPage()
        self._review_files_page_id = self.addPage(self._review_files_page)
        self._summary_page = ExportPage()
        self._summary_page_id = self.addPage(self._summary_page)

        self.currentIdChanged.connect(self._on_page_changed)

    @property
    def _device_state(self):
        self._device.state

    def _on_device_missing(self) -> None:
        current_page_id = self.currentId()
        if current_page_id > self._insert_device_page_id and current_page_id < self._summary_page_id:
            lastId = self.currentId()
            while self.currentId() != self._insert_device_page_id and self.currentId != lastId:
                lastId = self.currentId()
                self.back()

    @pyqtSlot()  # I'm not sure this one needs to be a slot, but I'll err on the side of caution.
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
        self._unlock_device_page.isComplete()
