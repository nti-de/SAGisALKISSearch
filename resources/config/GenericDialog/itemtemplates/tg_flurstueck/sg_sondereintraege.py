from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QFormLayout

from ...... import commonfunctions
from ......resultdialog.dialogitem import DialogItem
from ......sagisgndlgconfig.configcontext import ConfigContext
from ......sagisgndlgconfig.sagis_gn_dlg_config import SagisGnDlgConfig


class SG_SONDEREINTRAEGE(DialogItem):
    def __init__(self, context: ConfigContext,
                 panel: SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel,
                 data: dict, object_index=-1, total_objects=0, parent=None):
        super().__init__(context, panel, data, object_index, total_objects, parent)

        self.setLayout(QFormLayout())
        self.layout().setHorizontalSpacing(64)

        self.labelCurrentIndex = QLabel()
        self.labelCurrentIndex.setStyleSheet("background-color: #fbf696")
        self.layout().addRow(self.labelCurrentIndex)

        self.labelFlurstueckkennzeichen = QLabel()
        self.labelSondereintrag = QLabel()
        self.labelTyp = QLabel()
        self.labelBezeichnung = QLabel()
        self.labelAktiv = QLabel()
        self.labelVonBis = QLabel()
        self.labelErstellt = QLabel()
        self.labelGeaendert = QLabel()

        self.layout().addRow("Flurstückskennzeichen:", self.labelFlurstueckkennzeichen)
        self.layout().addRow("Sondereintrag:", self.labelSondereintrag)
        self.layout().addRow("Typ:", self.labelTyp)
        self.layout().addRow("Bezeichnung:", self.labelBezeichnung)
        self.layout().addRow("Aktiv:", self.labelAktiv)
        self.layout().addRow("Von / Bis:", self.labelVonBis)
        self.layout().addRow("Erstellt:", self.labelErstellt)
        self.layout().addRow("Geändert:", self.labelGeaendert)

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
        # Flurstückskennzeichen
        self.labelFlurstueckkennzeichen.setText(self.get_value("flurstueckskennzeichen", ""))

        # Sondereintrag
        self.labelSondereintrag.setText(self.get_value("sondereintrag", ""))

        # Typ
        self.labelTyp.setText(self.get_value("typ_tbd_value", ""))

        # Bezeichnung
        self.labelBezeichnung.setText(self.get_value("bezeichnung", ""))

        # Aktiv
        self.labelAktiv.setText(
            "Ja" if str(self.get_value("aktiv", "")) in ["True", "t", "j", "x", "1", "ja", "yes", "wahr", "on", "true"] else "Nein"
        )

        # Von / Bis
        self.labelVonBis.setText(
            f"{commonfunctions.test_date(self.get_value('aktiv_ab', ''))} - "
            f"{commonfunctions.test_date(self.get_value('aktiv_bis', ''))}"
        )

        # Erstellt
        self.labelErstellt.setText(
            f"{commonfunctions.test_date(self.get_value('sg_insrtdat', ''))}, von: "
            f"{self.get_value('sg_insrtuser', '')}"
        )

        # Geändert
        self.labelGeaendert.setText(
            f"{commonfunctions.test_date(self.get_value('sg_updtdat', ''))}, von: "
            f"{self.get_value('sg_updtuser', '')}"
        )
