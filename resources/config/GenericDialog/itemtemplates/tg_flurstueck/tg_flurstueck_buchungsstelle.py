from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QFormLayout

from ...... import commonfunctions
from ......resultdialog.dialogbindingwidget import DialogBindingWidget
from ......resultdialog.dialogitem import DialogItem
from ......sagisgndlgconfig.configcontext import ConfigContext
from ......sagisgndlgconfig.sagis_gn_dlg_config import SagisGnDlgConfig


class TG_FLURSTUECK_BUCHUNGSSTELLE(DialogItem):
    def __init__(self, context: ConfigContext,
                 panel: SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel,
                 data: dict, object_index=-1, total_objects=0, parent=None):
        super().__init__(context, panel, data, object_index, total_objects, parent)

        self.setLayout(QFormLayout())
        self.layout().setHorizontalSpacing(64)

        self.labelCurrentIndex = QLabel()
        self.labelCurrentIndex.setStyleSheet("background-color: #fbf696")
        self.layout().addRow(self.labelCurrentIndex)

        self.labelLfdNr = QLabel()
        self.labelAnteil = QLabel()
        self.labelBeginnEnde = QLabel()
        self.labelBuchungsart = QLabel()

        self.layout().addRow("Lfd.-Nr.:", self.labelLfdNr)
        self.layout().addRow("Anteil:", self.labelAnteil)
        self.layout().addRow("Beginn/Ende:", self.labelBeginnEnde)
        self.layout().addRow("Buchungsart:", self.labelBuchungsart)

        bold_font = self.labelCurrentIndex.font()
        bold_font.setBold(True)
        self.labelCurrentIndex.setFont(bold_font)

        for i in range(self.layout().rowCount()):
            item = self.layout().itemAt(i, QFormLayout.LabelRole)
            if item:
                item.widget().setFont(bold_font)
                item.widget().setFixedHeight(13)

            item = self.layout().itemAt(i, QFormLayout.FieldRole)
            if item and isinstance(item.widget(), QLabel):
                item.widget().setTextInteractionFlags(item.widget().textInteractionFlags() | Qt.TextSelectableByMouse)
                item.widget().setFixedHeight(13)

        # Bindings
        self.data_gvBuchungsblaetter = DialogBindingWidget()
        self.data_gvAnlass = DialogBindingWidget()

        self.layout().addRow(self.data_gvBuchungsblaetter)
        self.layout().addRow(self.data_gvAnlass)

    def set_label_texts(self):
        # Buchungsart
        self.labelLfdNr.setText(self.get_value("lnr", ""))

        # Anteil
        self.labelAnteil.setText(
            f"{commonfunctions.get_formatted_string(self.get_value('ant_zae', ''))}/"
            f"{commonfunctions.get_formatted_string(self.get_value('ant_nen', ''))}"
        )

        # Endet
        self.labelBeginnEnde.setText(
            f"{commonfunctions.test_date(self.get_value('beginnt', ''))}/"
            f"{commonfunctions.test_date(self.get_value('endet', ''))}"
        )

        self.labelBuchungsart.setText(
            f"{self.get_value('bs_bart', '')}/"
            f"{self.get_value('bs_bart_text', '')}"
        )
