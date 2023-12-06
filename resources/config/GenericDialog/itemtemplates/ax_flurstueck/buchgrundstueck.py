from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QFormLayout

from ...... import commonfunctions
from ......resultdialog.dialogbindingwidget import DialogBindingWidget
from ......resultdialog.dialogitem import DialogItem
from ......sagisgndlgconfig.configcontext import ConfigContext
from ......sagisgndlgconfig.sagis_gn_dlg_config import SagisGnDlgConfig


class BUCHGRUNDSTUECK(DialogItem):
    def __init__(self, context: ConfigContext,
                 panel: SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel,
                 data: dict, object_index=-1, total_objects=0, parent=None):
        super().__init__(context, panel, data, object_index, total_objects, parent)

        self.labelFlurstueckskennzeichen = QLabel()
        self.labelGemarkung = QLabel()
        self.labelFlurZaehlerNenner = QLabel()
        self.labelAmtlicheFlaeche = QLabel()

        self.setLayout(QFormLayout())
        self.layout().setHorizontalSpacing(64)

        self.layout().addRow("Flurstückskennzeichen:", self.labelFlurstueckskennzeichen)
        self.layout().addRow("Gemarkung:", self.labelGemarkung)
        self.layout().addRow("Flur / Zähler / Nenner:", self.labelFlurZaehlerNenner)
        self.layout().addRow("Amtl. Fläche:", self.labelAmtlicheFlaeche)

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

    def set_label_texts(self):
        self.labelFlurstueckskennzeichen.setText(
            f"{self.get_value('flurstueckskennzeichen')}"
        )

        self.labelGemarkung.setText(
            f"{self.get_value('gmk_schluesselgesamt')}/{self.get_value('gemarkungbezeichnung')}"
        )

        self.labelFlurZaehlerNenner.setText(
            f"{self.get_value('flurnummer')}/{self.get_value('flurstuecksnummer_zaehler')}/{self.get_value('flurstuecksnummer_nenner')}"
        )

        self.labelAmtlicheFlaeche.setText(
            f"{commonfunctions.get_formatted_string(self.get_value('amtlicheflaeche'))} m²"
        )
