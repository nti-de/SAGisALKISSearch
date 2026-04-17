from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QFormLayout

from ...... import commonfunctions
from ......resultdialog.dialogbindingwidget import DialogBindingWidget
from ......resultdialog.dialogitem import DialogItem
from ......sagisgndlgconfig.configcontext import ConfigContext
from ......sagisgndlgconfig.sagis_gn_dlg_config import SagisGnDlgConfig


class AX_FLURSTUECK(DialogItem):
    def __init__(self, context: ConfigContext,
                 panel: SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel,
                 data: dict, object_index=-1, total_objects=0, parent=None):
        super().__init__(context, panel, data, object_index, total_objects, parent)

        self.labelGemeindeZugehoerigkeit = QLabel()
        self.labelEntstehung = QLabel()
        self.labelGemarkung = QLabel()
        self.labelamtlicheFlaeche = QLabel()
        self.labelFlurZaehlerNenner = QLabel()
        self.labelFlaecheKarte = QLabel()
        self.labelFlurstueckKennzeichen = QLabel()
        self.labelAlkisId = QLabel()

        self.setLayout(QFormLayout())
        self.layout().setHorizontalSpacing(64)

        self.layout().addRow("Flurstückskennzeichen:", self.labelFlurstueckKennzeichen)
        self.layout().addRow("Gemeinde:", self.labelGemeindeZugehoerigkeit)
        self.layout().addRow("Gemarkung:", self.labelGemarkung)
        self.layout().addRow("Flur / Zähler / Nenner:", self.labelFlurZaehlerNenner)
        self.layout().addRow("Entstehung:", self.labelEntstehung)
        self.layout().addRow("amtliche Fläche [m²]:", self.labelamtlicheFlaeche)
        self.layout().addRow("Fläche in der Karte [m²]:", self.labelFlaecheKarte)
        self.layout().addRow("Alkis-ID:", self.labelAlkisId)

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
        self.dataLETZTEAUSLEITUNG = DialogBindingWidget()

        self.dataV_EIGENTUEMER_DIST_OVERVIEW = DialogBindingWidget()
        self.data_gvNutzung = DialogBindingWidget()
        self.data_gvLagebezeichnung = DialogBindingWidget()

        self.layout().addRow(self.dataLETZTEAUSLEITUNG)
        self.layout().addRow(self.dataV_EIGENTUEMER_DIST_OVERVIEW)
        self.layout().addRow(self.data_gvNutzung)
        self.layout().addRow(self.data_gvLagebezeichnung)

    def set_label_texts(self):
        self.labelGemeindeZugehoerigkeit.setText(
            f"{self.get_value('gemeindeschluessel')}/{self.get_value('gemeindebezeichnung')}"
        )

        self.labelEntstehung.setText(
            f"{commonfunctions.test_date(self.get_value('zeitpunktderentstehung'))}"
        )

        self.labelGemarkung.setText(
            f"{self.get_value('gemarkungschluessel')}/{self.get_value('gemarkungbezeichnung')}"
        )

        self.labelamtlicheFlaeche.setText(
            f"{commonfunctions.get_formatted_string(self.get_value('amtlicheflaeche'), 2)}"
        )

        self.labelFlurZaehlerNenner.setText(
            f"{self.get_value('flurnummer')}/{self.get_value('flurstuecksnummer_zaehler')}/{self.get_value('flurstuecksnummer_nenner')}"
        )

        self.labelFlaecheKarte.setText(
            f"{commonfunctions.get_formatted_string(self.get_value('area'), 2)} "
            f"(Abweichung: "
            f"{str(commonfunctions.get_formatted_string(self.get_value('x_area_diff_perc'), 2))}"
            f"%)"
        )

        self.labelFlurstueckKennzeichen.setText(
            f"{self.get_value('flurstueckskennzeichen')}"
        )

        self.labelAlkisId.setText(
            f"{self.get_value('id')}"
        )
