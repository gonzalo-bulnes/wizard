from typing import NewType

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from state_transitions import SpecificKeyEventTransition, SpecificMouseButtonEventTransition


class DialogState(QWidget):
    """The state of a multi-page wizard.

    There should be no need for you to use this class directly.

    Paste the following state chart in https://mermaid.live for
    a visual representation of the behavior implemented by this class!

    stateDiagram-v2
      %% To be documented.
    """

    def __init__(self, dialog: "Dialog") -> None:
        super().__init__()

        self._dialog = dialog

        # Declare the state chart described in the docstring.
        # See https://doc.qt.io/qt-5/statemachine-api.html
        #
        # This is a very declarative exercise.
        # The state names are part of the API of this class.
        self._machine = QStateMachine()

        # ...

        self._machine.start()


class Dialog(QDialog):
    """
    A multi-page wizard, with a banner.

    While this widget looks and behaves in a specific way,
    the custom behavior was implemented to avoid obstructing the QDialog API.
    This means all accessibility features of a QDialog should be available.

    This widget also emits all the events that a regular QDialog emits.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.state = DialogState(self)
        self.banner = Banner()

        with open("dialog.css", "r") as stylesheet:
            self.setStyleSheet(stylesheet.read())
