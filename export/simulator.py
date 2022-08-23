import sys
from typing import List

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from buttons import PushButton
from .service import Service as ExportService

LOADING_TIME_IN_MS = 1500

class Simulator(QWidget):
    """A USB device simulator"""
    def __init__(self, service: ExportService, parent=None):
        super().__init__(parent)

        self._service = service

        # Connect the device.
        self._service.started.connect(self._on_export_started)
        self._service.finished.connect(self._on_export_finished)
        
        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        title = QLabel("<h1>Export Simulator</h1>")
        layout.addWidget(title)
        status = QLabel("<p>Creating some more suspense...</p>")
        status.setWordWrap(True)
        layout.addWidget(status)
        layout.setSizeConstraint(QLayout.SetFixedSize)

        self._status = status

        simulateExportSuccess, simulateExportFailure = self._create_buttons()
        self._buttons = {}
        self._buttons["idle"] = []
        self._buttons["exporting"] = [simulateExportSuccess, simulateExportFailure]
        self._buttons["all"] = [simulateExportSuccess, simulateExportFailure]
        
        self._initialize_export_service()
        self.show()


    def _create_buttons(self) -> List[PushButton]:

        simulateExportSuccess = PushButton(PushButton.TypeContained)
        simulateExportSuccess.setText("SIMULATE EXPORT SUCCESS")
        simulateExportSuccess.clicked.connect(self._on_export_success_simulated)
        self.layout().addWidget(simulateExportSuccess)
        simulateExportSuccess.setEnabled(False)
        simulateExportSuccess.hide()

        simulateExportFailure = PushButton(PushButton.TypeOutlined)
        simulateExportFailure.setText("SIMULATE EXPORT FAILURE")
        simulateExportFailure.clicked.connect(self._on_export_failure_simulated)
        self.layout().addWidget(simulateExportFailure)
        simulateExportFailure.setEnabled(False)
        simulateExportFailure.hide()

        return [simulateExportSuccess, simulateExportFailure]

    def _initialize_export_service(self) -> None:
        timer = QTimer()
        timer.timeout.connect(lambda: self._service.check(ExportService.EmitFinished))
        timer.timeout.connect(lambda: self._timer.stop())
        timer.start(LOADING_TIME_IN_MS)
        self._timer = timer

    def _on_export_started(self) -> None:
        self._status.setText("Data is being exported...")
        for button in self._buttons["all"]:
            button.hide()
            button.setEnabled(False)
        for button in self._buttons["exporting"]:
            button.show()
            button.setEnabled(True)

    def _on_export_finished(self) -> None:
        self._status.setText("Options will become available as soon as data is being exported.")
        for button in self._buttons["all"]:
            button.hide()
            button.setEnabled(False)
        for button in self._buttons["idle"]:
            button.show()
            button.setEnabled(True)

    def _on_export_failure_simulated(self) -> None:
        self._service.check(ExportService.EmitFailed)

    def _on_export_success_simulated(self) -> None:
        self._service.check(ExportService.EmitSucceeded)
