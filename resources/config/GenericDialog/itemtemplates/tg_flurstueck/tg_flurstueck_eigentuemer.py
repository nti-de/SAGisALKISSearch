from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QFormLayout

from ...... import commonfunctions
from ......resultdialog.dialogbindingwidget import DialogBindingWidget
from ......resultdialog.dialogitem import DialogItem
from ......sagisgndlgconfig.configcontext import ConfigContext
from ......sagisgndlgconfig.sagis_gn_dlg_config import SagisGnDlgConfig


class TG_FLURSTUECK_EIGENTUEMER(DialogItem):
    def __init__(self, context: ConfigContext,
                 panel: SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel,
                 data: dict, object_index=-1, total_objects=0, parent=None):
        super().__init__(context, panel, data, object_index, total_objects, parent)

        self.setLayout(QFormLayout())
        self.layout().setHorizontalSpacing(64)

        self.labelCurrentIndex = QLabel()
        self.labelCurrentIndex.setStyleSheet("background-color: #fbf696")
        self.layout().addRow(self.labelCurrentIndex)

        self.labelBuchungsart = QLabel()
        self.labelLfdNr = QLabel()
        self.labelAnteil = QLabel()
        self.labelBuchungsblattKennzeichen = QLabel()
        self.labelBuchungsblattBezirk = QLabel()
        self.labelBlattart = QLabel()
        self.labelNamensnummer = QLabel()
        self.labelAnteilsVerhaeltnis = QLabel()
        self.labelEigentuemerart = QLabel()
        self.labelAnrede = QLabel()
        self.labelGeburtsname = QLabel()
        self.labelGeburtsdatum = QLabel()

        self.layout().addRow("Buchungsart:", self.labelBuchungsart)
        self.layout().addRow("Laufende Nummer:", self.labelLfdNr)
        self.layout().addRow("Anteil Miteigentum:", self.labelAnteil)
        self.layout().addRow("Buchungsblattkennzeichen:", self.labelBuchungsblattKennzeichen)
        self.layout().addRow("Buchungsblattbezirk/-nummer:", self.labelBuchungsblattBezirk)
        self.layout().addRow("Blattart:", self.labelBlattart)
        self.layout().addRow("Namensnummer:", self.labelNamensnummer)
        self.layout().addRow("Anteilsverhältnis:", self.labelAnteilsVerhaeltnis)
        self.layout().addRow("Eigentümerart:", self.labelEigentuemerart)
        self.layout().addRow("Anrede Nachname (Firma), Vorname:", self.labelAnrede)
        self.layout().addRow("Geburtsname:", self.labelGeburtsname)
        self.layout().addRow("Geburtsdatum:", self.labelGeburtsdatum)

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

        # Bindings
        self.dataANSCHRIFT_PERSON = DialogBindingWidget()

        self.layout().addRow(self.dataANSCHRIFT_PERSON)

    def set_label_texts(self):
        # Buchungsart (Buchungsstelle)
        self.labelBuchungsart.setText(
            f"{self.get_value('bs_bart', '')}/"
            f"{self.get_value('bs_bart_text', '')}"
        )

        # Laufende Nummer (Buchungsstelle)
        self.labelLfdNr.setText(self.get_value("bs_lnr", ""))

        # Anteil Miteigentum (Buchungsstelle)
        self.labelAnteil.setText(
            f"{commonfunctions.get_formatted_string(self.get_value('bs_miteig_ant_zae', ''))}/"
            f"{commonfunctions.get_formatted_string(self.get_value('bs_miteig_ant_nen', ''))}"
        )

        # Buchungsblattkennz
        self.labelBuchungsblattKennzeichen.setText(self.get_value("bblatt_kennz", ""))

        # Buchungsblattbezirk/-nummer
        self.labelBuchungsblattBezirk.setText(
            f"{self.get_value('bblatt_bezirk', '')}/"
            f"{self.get_value('bblatt_bezirk_text', '')} "
            f"{self.get_value('bblatt_nummer', '')}"
        )

        # Blattart
        self.labelBlattart.setText(
            f"{self.get_value('bblatt_bart', '')}/"
            f"{self.get_value('bblarr_bart_text', '')}"
        )

        # Namensnummer
        self.labelNamensnummer.setText(self.get_value("nnummer_lnr", ""))

        # Anteilsverhältnis
        self.labelAnteilsVerhaeltnis.setText(
            f"{commonfunctions.get_formatted_string(self.get_value('nnummer_ant_zae', ''))}/"
            f"{commonfunctions.get_formatted_string(self.get_value('nnummer_ant_nen', ''))}"
        )

        # Eigentümerart
        self.labelEigentuemerart.setText(
            f"{self.get_value('nnummer_eigentuemerart', '')}/"
            f"{self.get_value('nnummer_eigentuemerart_text', '')}"
        )

        #  Anrede Nachname (Firma), Vorname
        self.labelAnrede.setText(
            f"{self.get_value('person_anrede_text', '')} "
            f"{self.get_value('person_akad_grad', '')}"
            f"{'' if not self.get_value('person_akad_grad', '') else ' '}"  # In SAGis web there is just a space
            f"{self.get_value('person_name', '')}"
            f"{'' if not self.get_value('person_vorname', '') else ', '}"
            f"{self.get_value('person_vorname', '')}"
        )

        # Geburtsname
        self.labelGeburtsname.setText(self.get_value("person_geburtsname", ""))
        self.labelGeburtsdatum.setText(commonfunctions.test_date(self.get_value("person_geburtsdatum", "")))
