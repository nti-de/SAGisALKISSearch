from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QFormLayout

from ...... import commonfunctions
from ......resultdialog.dialogbindingwidget import DialogBindingWidget
from ......resultdialog.dialogitem import DialogItem
from ......sagisgndlgconfig.configcontext import ConfigContext
from ......sagisgndlgconfig.sagis_gn_dlg_config import SagisGnDlgConfig


class SDO_RELATE_NUTZART(DialogItem):
    def __init__(self, context: ConfigContext,
                 panel: SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel,
                 data: dict, object_index=-1, total_objects=0, parent=None):
        super().__init__(context, panel, data, object_index, total_objects, parent)

        self.labelAnteilAmtlich1 = QLabel()
        self.labelAnteilAmtlich2 = QLabel()
        self.labelAnteilGeometrisch1 = QLabel()
        self.labelAnteilGeometrisch2 = QLabel()
        self.labelNutzungsart = QLabel()
        self.labelNutzungsunterart = QLabel()

        self.setLayout(QFormLayout())
        self.layout().setHorizontalSpacing(64)

        self.layout().addRow(self.labelAnteilAmtlich1, self.labelAnteilAmtlich2)
        self.layout().addRow(self.labelAnteilGeometrisch1, self.labelAnteilGeometrisch2)
        self.layout().addRow("Nutzungsart:", self.labelNutzungsart)
        self.layout().addRow("Nutzungsunterart", self.labelNutzungsunterart)

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
        self.labelAnteilAmtlich1.setText(
            f"Anteilige Fläche basierend auf Amtlicher Flurstücksfläche von {commonfunctions.get_formatted_string(self.get_value('amtlicheflaeche'))} m²"
        )

        self.labelAnteilAmtlich2.setText(
            f"{commonfunctions.get_formatted_string(self.get_value('tfl_amtlich'))} m² / {commonfunctions.get_formatted_string(self.get_value('amtl_flaecheanteil'))}"
        )

        self.labelAnteilGeometrisch1.setText(
            f"Anteilige Fläche basierend auf Geometrischer Flurstücksfläche von {commonfunctions.get_formatted_string(self.get_value('x_area_source'))} m²"
        )

        self.labelAnteilGeometrisch2.setText(
            f"{commonfunctions.get_formatted_string(self.get_value('x_area_intersection'))} m² / {commonfunctions.get_formatted_string(self.get_value('flaecheanteil'))}"
        )

        self.labelNutzungsart.setText(
            f"{'keine Angabe' if not self.get_value('art_tabelle_text') else self.get_value('art_tabelle_text')}"
        )

        self.labelNutzungsunterart.setText(
            f"{'keine Angabe' if not self.get_value('x_subtype_value') else self.get_value('x_subtype_value')}"
        )
