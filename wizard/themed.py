from PyQt5.QtWidgets import QWidget

import export
from device import Device
from buttons import PushButton

from .main import Wizard

class ThemedWizard(Wizard):

    def __init__(self, device: Device, export_service: export.Service, parent: QWidget =None):
        super().__init__(device, export_service, parent)

        self.setOption(Wizard.CancelButtonOnLeft)

        button = PushButton(PushButton.TypeContained)
        button.setText("CONTINUE")
        self.setButton(Wizard.WizardButton.NextButton, button)

        button = PushButton(PushButton.TypeOutlined)
        button.setText("BACK")
        self.setButton(Wizard.WizardButton.BackButton, button)

        button = PushButton(PushButton.TypeText)
        button.setText("CANCEL")
        self.setButton(Wizard.WizardButton.CancelButton, button)

        button = PushButton(PushButton.TypeContained)
        button.setText("FINISH")
        self.setButton(Wizard.WizardButton.FinishButton, button)

        self.setButtonLayout([
            Wizard.WizardButton.CancelButton,
            Wizard.WizardButton.Stretch,
            Wizard.WizardButton.BackButton,
            Wizard.WizardButton.NextButton,
            Wizard.WizardButton.FinishButton,
        ])

