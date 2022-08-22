from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ExportPage(QWizardPage):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Done!")

        content = QLabel("Your files were exported successfully.")
        content.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(content)
        self.setLayout(layout)
