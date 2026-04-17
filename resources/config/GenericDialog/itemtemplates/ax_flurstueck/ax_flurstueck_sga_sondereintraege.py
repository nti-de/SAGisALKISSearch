from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QLabel, QFormLayout

from ...... import commonfunctions
from ......resultdialog.dialogitem import DialogItem
from ......sagisgndlgconfig.configcontext import ConfigContext
from ......sagisgndlgconfig.sagis_gn_dlg_config import SagisGnDlgConfig


class AX_FLURSTUECK_SGA_SONDEREINTRAEGE(DialogItem):
    def __init__(self, context: ConfigContext,
                 panel: SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel,
                 data: dict, object_index=-1, total_objects=0, parent=None):
        super().__init__(context, panel, data, object_index, total_objects, parent)

        self.setLayout(QFormLayout())
        self.layout().setHorizontalSpacing(64)

        self.labelSondereintrag = QLabel()
        self.labelTyp = QLabel()
        self.labelAktiv = QLabel()
        self.labelVonBis = QLabel()
        self.labelErstellt = QLabel()
        self.labelGeaendert = QLabel()

        self.layout().addRow("Sondereintrag:", self.labelSondereintrag)
        self.layout().addRow("Typ:", self.labelTyp)
        self.layout().addRow("Aktiv:", self.labelAktiv)
        self.layout().addRow("Von / Bis:", self.labelVonBis)
        self.layout().addRow("Erstellt:", self.labelErstellt)
        self.layout().addRow("Geändert:", self.labelGeaendert)

        bold_font = self.labelCurrentIndex.font()
        bold_font.setBold(True)
        self.labelCurrentIndex.setFont(bold_font)

        for i in range(self.layout().rowCount()):
            item = self.layout().itemAt(i, QFormLayout.ItemRole.LabelRole)
            if item:
                item.widget().setFont(bold_font)

            item = self.layout().itemAt(i, QFormLayout.ItemRole.FieldRole)
            if item and isinstance(item.widget(), QLabel):
                item.widget().setTextInteractionFlags(item.widget().textInteractionFlags() | Qt.TextInteractionFlag.TextSelectableByMouse)

    def set_label_texts(self):
        # Sondereintrag
        sondereintrag = self.get_value("sondereintrag")
        self.labelSondereintrag.setText(
            "[Kein Wert eingegeben]" if not sondereintrag else sondereintrag
        )

        # Typ
        self.labelTyp.setText(self.get_value("typ_tbd_value", ""))

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
            f"{commonfunctions.test_date(self.get_value('sg_insrtdat', ''))}"
            f", von: "
            f"{self.get_value('sg_insrtuser', '')}"
        )

        # Geändert
        self.labelGeaendert.setText(
            f"{commonfunctions.test_date(self.get_value('sg_updtdat', ''))}"
            f", von: "
            f"{self.get_value('sg_updtuser', '')}"
        )
