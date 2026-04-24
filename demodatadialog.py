import os

from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt import uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "ui/demodata.ui"))


class DemoDataDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
