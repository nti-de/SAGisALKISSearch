from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QFormLayout

from ...... import commonfunctions
from ......resultdialog.dialogbindingwidget import DialogBindingWidget
from ......resultdialog.dialogitem import DialogItem
from ......sagisgndlgconfig.configcontext import ConfigContext
from ......sagisgndlgconfig.sagis_gn_dlg_config import SagisGnDlgConfig


class BUCHUNGSSTELLEN(DialogItem):
    def __init__(self, context: ConfigContext,
                 panel: SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel,
                 data: dict, object_index=-1, total_objects=0, parent=None):
        super().__init__(context, panel, data, object_index, total_objects, parent)

        self.labelLfdNr = QLabel()
        self.labelAnteil = QLabel()
        self.labelBeginn = QLabel()
        self.labelBuchungsart = QLabel()

        self.setLayout(QFormLayout())
        self.layout().setHorizontalSpacing(64)

        self.layout().addRow("Lfd.-Nr.:", self.labelLfdNr)
        self.layout().addRow("Anteil:", self.labelAnteil)
        self.layout().addRow("Beginn:", self.labelBeginn)
        self.layout().addRow("Buchungsart:", self.labelBuchungsart)

        for i in range(self.layout().rowCount()):
            item = self.layout().itemAt(i, QFormLayout.LabelRole)
            if item:
                label = item.widget()
                font = label.font()
                font.setBold(True)
                item.widget().setFont(font)

            item = self.layout().itemAt(i, QFormLayout.FieldRole)
            if item and isinstance(item.widget(), QLabel):
                item.widget().setTextInteractionFlags(item.widget().textInteractionFlags() | Qt.TextSelectableByMouse)

        # Bindings
        self.dataBS_BUCHUNGSBLATT = DialogBindingWidget()

        self.layout().addRow(self.dataBS_BUCHUNGSBLATT)

    def set_label_texts(self):
        self.labelLfdNr.setText(
            f"{self.get_value('laufendenummer')}"
        )

        self.labelAnteil.setText(
            f"{commonfunctions.get_formatted_string(self.get_value('anteil_zaehler'))}/"
            f"{commonfunctions.get_formatted_string(self.get_value('anteil_nenner'))}"
        )

        self.labelBeginn.setText(
            f"{commonfunctions.test_date(self.get_value('lzb'))}"
        )

        self.labelBuchungsart.setText(
            f"{self.get_value('buchungsart')} - {self.get_value('buchungsart_value')}"
        )
