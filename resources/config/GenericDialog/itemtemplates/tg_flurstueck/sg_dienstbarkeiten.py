from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QFormLayout

from ......resultdialog.dialogitem import DialogItem
from ......sagisgndlgconfig.configcontext import ConfigContext
from ......sagisgndlgconfig.sagis_gn_dlg_config import SagisGnDlgConfig


class SG_DIENSTBARKEITEN(DialogItem):
    def __init__(self, context: ConfigContext,
                 panel: SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel,
                 data: dict, object_index=-1, total_objects=0, parent=None):
        super().__init__(context, panel, data, object_index, total_objects, parent)

        self.setLayout(QFormLayout())
        self.layout().setHorizontalSpacing(64)

        self.labelCurrentIndex = QLabel()
        self.labelCurrentIndex.setStyleSheet("background-color: #fbf696")
        self.layout().addRow(self.labelCurrentIndex)

        self.labelBezeichnung = QLabel()
        self.labelArt = QLabel()

        self.layout().addRow("Bezeichnung:", self.labelBezeichnung)
        self.layout().addRow("Art:", self.labelArt)

        bold_font = self.labelCurrentIndex.font()
        bold_font.setBold(True)
        self.labelCurrentIndex.setFont(bold_font)

        for i in range(self.layout().rowCount()):
            item = self.layout().itemAt(i, QFormLayout.LabelRole)
            if item:
                item.widget().setFont(bold_font)

            item = self.layout().itemAt(i, QFormLayout.FieldRole)
            if item and isinstance(item.widget(), QLabel):
                item.widget().setTextInteractionFlags(item.widget().textInteractionFlags() | Qt.TextSelectableByMouse)

    def set_label_texts(self):
        # Bezeichnung
        self.labelBezeichnung.setText(self.get_value("bezeichnung", ""))
        self.labelArt.setText(self.get_value("status_value", ""))
