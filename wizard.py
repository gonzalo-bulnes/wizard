from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Wizard(QWizard):
    def __init__(self, device, parent=None):
        super().__init__(parent)

        self._device = device

        self.setWindowTitle("Wizard")
        self.setModal(False)

        self.addPage(self._create_disclaimer_page())
        self.addPage(self._create_export_page())
        self.addPage(self._create_summary_page())

    def _create_disclaimer_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle("Disclaimer")

        content = QLabel("Please be aware that exporting files carries some <b>risks</b>.")
        content.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(content)
        page.setLayout(layout)

        return page

    def _create_export_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle("Unlock your device")

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
