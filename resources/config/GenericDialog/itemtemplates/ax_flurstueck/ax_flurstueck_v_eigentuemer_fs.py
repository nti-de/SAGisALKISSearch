from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QLabel, QFormLayout

from ...... import commonfunctions
from ......resultdialog.dialogbindingwidget import DialogBindingWidget
from ......resultdialog.dialogitem import DialogItem
from ......sagisgndlgconfig.configcontext import ConfigContext
from ......sagisgndlgconfig.sagis_gn_dlg_config import SagisGnDlgConfig


class AX_FLURSTUECK_V_EIGENTUEMER_FS(DialogItem):
    def __init__(self, context: ConfigContext,
                 panel: SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel,
                 data: dict, object_index=-1, total_objects=0, parent=None):
        super().__init__(context, panel, data, object_index, total_objects, parent)

        self.setLayout(QFormLayout())
        self.layout().setHorizontalSpacing(64)

        self.labelCurrentIndex = QLabel()
        self.labelCurrentIndex.setStyleSheet("background-color: #fbf696")
        self.layout().addRow(self.labelCurrentIndex)

        self.labelNamensnummer = QLabel()
        self.labelBuchungsblattKennz = QLabel()
        self.labelBuchungsblattBezirknummer = QLabel()
        self.labelBuchungsart = QLabel()
        self.labelAnteilBuchstelle = QLabel()
        self.labelAnrede = QLabel()
        self.labelAkademischerGrad = QLabel()
        self.labelVorname = QLabel()
        self.labelNachnameFirma = QLabel()
        self.labelGeburtsname = QLabel()
        self.labelNamensbestandteil = QLabel()
        self.labelGeburtsdatum = QLabel()
        self.labelAnteilsverhaeltnis = QLabel()
        self.labelEigentuemerart = QLabel()

        self.layout().addRow("Namensnummer nach DIN1421:", self.labelNamensnummer)
        self.layout().addRow("Buchungsblattkennzeichen.:", self.labelBuchungsblattKennz)
        self.layout().addRow("Buchungsblattbezirk/-nummer:", self.labelBuchungsblattBezirknummer)
        self.layout().addRow("Buchungsart:", self.labelBuchungsart)
        self.layout().addRow("Anteil Buchungsstelle:", self.labelAnteilBuchstelle)
        self.layout().addRow("Anrede:", self.labelAnrede)
        self.layout().addRow("Akademischer Grad:", self.labelAkademischerGrad)
        self.layout().addRow("Vorname:", self.labelVorname)
        self.layout().addRow("Nachname / Firma:", self.labelNachnameFirma)
        self.layout().addRow("Geburtsname:", self.labelGeburtsname)
        self.layout().addRow("Namensbestandteil:", self.labelNamensbestandteil)
        self.layout().addRow("Geburtsdatum:", self.labelGeburtsdatum)
        self.layout().addRow("Anteilsverhältnis:", self.labelAnteilsverhaeltnis)
        self.layout().addRow("Eigentümerart:", self.labelEigentuemerart)

        for i in range(self.layout().rowCount()):
            item = self.layout().itemAt(i, QFormLayout.ItemRole.LabelRole)
            if item:
                label = item.widget()
                font = label.font()
                font.setBold(True)
                item.widget().setFont(font)

            item = self.layout().itemAt(i, QFormLayout.ItemRole.FieldRole)
            if item and isinstance(item.widget(), QLabel):
                item.widget().setTextInteractionFlags(item.widget().textInteractionFlags() | Qt.TextInteractionFlag.TextSelectableByMouse)

        # Bindings
        self.dataV_ANSCHRIFT_PE = DialogBindingWidget()

        self.layout().addRow(self.dataV_ANSCHRIFT_PE)

    def set_label_texts(self):
        self.labelNamensnummer.setText(
            f"{self.get_value('laufendenummernachdin1421')}"
        )

        self.labelBuchungsblattKennz.setText(
            f"{self.get_value('buchungsblattkennzeichen')}"
        )

        self.labelBuchungsblattBezirknummer.setText(
            f"{self.get_value('bb_bezirk_key')}"
            f"/"
            f"{self.get_value('bb_bezirk_value')}"
            f" "
            f"{self.get_value('buchungsblattnummermitbuch')}"
        )

        self.labelBuchungsart.setText(
            f"{self.get_value('buchungsart_value')}"
        )

        self.labelAnteilBuchstelle.setText(
            f"{commonfunctions.get_formatted_string(self.get_value('bs_anteil_zaehler'))}"
            f"/"
            f"{commonfunctions.get_formatted_string(self.get_value('bs_anteil_nenner'))}"
        )

        self.labelAnrede.setText(
            f"{self.get_value('anrede_value')}"
        )

        self.labelAkademischerGrad.setText(
            f"{self.get_value('akademischergrad')}"
        )

        self.labelVorname.setText(
            f"{self.get_value('vorname')}"
        )

        self.labelNachnameFirma.setText(
            f"{self.get_value('nachnameoderfirma')}"
        )

        self.labelGeburtsname.setText(
            f"{self.get_value('geburtsname')}"
        )

        self.labelNamensbestandteil.setText(
            f"{self.get_value('namensbestandteil')}"
        )

        self.labelGeburtsdatum.setText(
            f"{commonfunctions.test_date(self.get_value('geburtsdatum'))}"
        )

        self.labelAnteilsverhaeltnis.setText(
            f"{commonfunctions.get_formatted_string(self.get_value('anteil_zaehler'))}"
            f"/"
            f"{commonfunctions.get_formatted_string(self.get_value('anteil_nenner'))}"
        )

        self.labelEigentuemerart.setText(
            f"{self.get_value('eigentuemerart')}"
            f"/"
            f"{self.get_value('eigentuemerart_value')}"
        )
