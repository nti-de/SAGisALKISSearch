from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QFormLayout

from ...... import commonfunctions
from ......resultdialog.dialogbindingwidget import DialogBindingWidget
from ......resultdialog.dialogitem import DialogItem
from ......sagisgndlgconfig.configcontext import ConfigContext
from ......sagisgndlgconfig.sagis_gn_dlg_config import SagisGnDlgConfig


class AX_FLURSTUECK_SDO_RELATE_AX_GEBAEUDE(DialogItem):
    def __init__(self, context: ConfigContext,
                 panel: SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel,
                 data: dict, object_index=-1, total_objects=0, parent=None):
        super().__init__(context, panel, data, object_index, total_objects, parent)

        self.setLayout(QFormLayout())
        self.layout().setHorizontalSpacing(64)

        self.labelCurrentIndex = QLabel()
        self.labelCurrentIndex.setStyleSheet("background-color: #fbf696")
        self.layout().addRow(self.labelCurrentIndex)

        self.labelKennung = QLabel()
        self.labelFlaecheKarte = QLabel()
        self.labelAnteiligAufFlurstueck = QLabel()
        self.labelFunktion = QLabel()
        self.labelDachform = QLabel()
        self.labelFlaecheAbzueglichGebauede = QLabel()

        self.layout().addRow("Kennung:", self.labelKennung)
        self.layout().addRow("Fläche in der Karte:", self.labelFlaecheKarte)
        self.layout().addRow("Anteilig auf dem Flurstück:", self.labelAnteiligAufFlurstueck)
        self.layout().addRow("Funktion:", self.labelFunktion)
        self.layout().addRow("Dachform:", self.labelDachform)
        self.layout().addRow("Flurstücksfläche abzüglich Gebäudefläche(n) [m²]:", self.labelFlaecheAbzueglichGebauede)

        # Bindings
        self.data_gvLagebezeichnung = DialogBindingWidget()
        self.layout().addRow("Lagebezeichnung:", self.data_gvLagebezeichnung)

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
        # Kennung
        gebaeudekennzeichen = self.get_value('gebaeudekennzeichen')
        self.labelKennung.setText(
            f"{'Keine Angabe' if not gebaeudekennzeichen else gebaeudekennzeichen}"
        )

        # Fläche in der Karte
        self.labelFlaecheKarte.setText(
            f"{commonfunctions.get_formatted_string(self.get_value('x_area_target'), 2)}"
        )

        # Anteilig auf dem Flurstück [m²]
        try:
            x_area_intersection_float = float(self.get_value('x_area_intersection'))
            x_area_source_float = float(self.get_value('x_area_source'))
            result = commonfunctions.get_formatted_string(100 * x_area_intersection_float / x_area_source_float, 2)

            self.labelAnteiligAufFlurstueck.setText(
                f"{commonfunctions.get_formatted_string(x_area_intersection_float, 3)}"
                f" m² "
                f"{result}"
            )
        except:
            self.labelAnteiligAufFlurstueck.setText("")

        # Funktion
        self.labelFunktion.setText(
                f"{commonfunctions.get_formatted_string(self.get_value('x_gebaeudefunktion_value'), 2)}"
        )

        # Dachform
        self.labelDachform.setText(
            f"{commonfunctions.get_formatted_string(self.get_value('x_dachform_value'), 2)}"
        )

        # Flurstücksfläche abzüglich Gebäudefläche(n) [m²]
        x_area_source_float = float(self.get_value('x_area_source'))
        x_area_intersection_total_float = float(self.get_value('x_area_intersection_total'))

        value1 = commonfunctions.get_formatted_string(x_area_source_float - x_area_intersection_total_float, 3)
        value2 = commonfunctions.get_formatted_string(x_area_source_float, 3)
        value3 = commonfunctions.get_formatted_string(x_area_intersection_total_float, 3)
        value4 = commonfunctions.get_formatted_string(100 * x_area_intersection_total_float / x_area_source_float, 3)

        self.labelFlaecheAbzueglichGebauede.setText(
            f"{value1} ({value2} - {value3}) {value4}% an Gebäudefläche ggü. der Flurstücksfläche"
        )
