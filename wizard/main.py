from enum import IntEnum

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from device import Device
import export
from .pages import StartPage, InsertDevicePage, UnlockDevicePage, ReviewDataPage, ExportPage


class Wizard(QWizard):

    PageId = IntEnum('PageId', 'START INSERT_DEVICE UNLOCK_DEVICE REVIEW_DATA EXPORT')

    def __init__(self, device: Device, export_service: export.Service, parent=None):
        super().__init__(parent)

        # Connect the device
        self._device = device
        self._device.state_changed.connect(self._on_device_state_changed)

        self._export_service = export_service

        self.setWindowTitle("Wizard")
        self.setModal(False)
        self.setOptions(
            QWizard.NoBackButtonOnLastPage |
            QWizard.NoCancelButtonOnLastPage |
            QWizard.NoBackButtonOnStartPage
        )

        self.setPage(Wizard.PageId.START, StartPage())
        self.setPage(Wizard.PageId.INSERT_DEVICE, InsertDevicePage(self._device.state_changed))
        self.setPage(Wizard.PageId.UNLOCK_DEVICE, UnlockDevicePage(self._device))
        self.setPage(Wizard.PageId.REVIEW_DATA, ReviewDataPage())
        self.setPage(Wizard.PageId.EXPORT, ExportPage(self._export_service))

        self.setStartId(Wizard.PageId.START)

        self.currentIdChanged.connect(self._on_page_changed)

    @pyqtSlot(str)
    def _on_device_state_changed(self, state: Device.State) -> None:
        device_state = self._device.state
        page_id = self.currentId()

        # this method screams for thorough unit testing - the proof-of-concept works
        if device_state == Device.MissingState or device_state == Device.RemovedState:
            if page_id > Wizard.PageId.INSERT_DEVICE and page_id < Wizard.PageId.EXPORT:
                self._back_to_page(Wizard.PageId.INSERT_DEVICE)
        elif device_state == Device.UnlockedState or device_state == Device.UnknownState:
            pass
        else:
            if page_id > Wizard.PageId.UNLOCK_DEVICE and page_id < Wizard.PageId.EXPORT:
                self._back_to_page(Wizard.PageId.UNLOCK_DEVICE)

    def _back_to_page(self, id: "Wizard.PageId") -> None:
        while self.currentId() > id:  # assumes that pages are sorted by ID, which is true
            self.back()

    @pyqtSlot(int)
    def _on_page_changed(self, id: int) -> None:
        self._on_device_state_changed(self._device.state)  # very inelegant
