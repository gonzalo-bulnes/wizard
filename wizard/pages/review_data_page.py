from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ReviewDataPage(QWizardPage):
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Review file list")

        content = QLabel("The following files will be exported: ...")
        content.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(content)
        self.setLayout(layout)
