from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Wizard(QDialog):
    def __init__(self, device_present, device_adequate, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wizard")
        self.setModal(False)

