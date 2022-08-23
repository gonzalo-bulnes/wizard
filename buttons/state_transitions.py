from typing import NewType

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class SpecificKeyEventTransition(QEventTransition):
    """A transition that triggers only on a QKeyEvent for a specific key (e.g. Qt.Key_Space)."""
    def __init__(self, object: QObject, type: QEvent.Type, key: int, sourceState: QState = None) -> None:
        super().__init__(object, type, sourceState)
        self._key = key

    def eventTest(self, event: QEvent) -> bool:
        if super().eventTest(event):
            we: QStateMachine.WrappedEvent = event
            return we.event().key() == self._key
        return False


class SpecificMouseButtonEventTransition(QEventTransition):
    """A transition that triggers only on a QMouseEvent for a specific button (e.g. Qt.LeftButton)."""
    def __init__(self, object: QObject, type: QEvent.Type, button: int, sourceState: QState = None) -> None:
        super().__init__(object, type, sourceState)
        self._button = button

    def eventTest(self, event: QEvent) -> bool:
        if super().eventTest(event):
            we: QStateMachine.WrappedEvent = event
            return we.event().button() == self._button
        return False
