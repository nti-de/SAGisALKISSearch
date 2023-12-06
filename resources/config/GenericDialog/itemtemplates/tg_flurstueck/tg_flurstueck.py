from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QFormLayout

from ...... import commonfunctions
from ......resultdialog.dialogbindingwidget import DialogBindingWidget
from ......resultdialog.dialogitem import DialogItem
from ......sagisgndlgconfig.configcontext import ConfigContext
from ......sagisgndlgconfig.sagis_gn_dlg_config import SagisGnDlgConfig


class TG_FLURSTUECK(DialogItem):
    def __init__(self, context: ConfigContext,
                 panel: SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel,
                 data: dict, object_index=-1, total_objects=0, parent=None):
        super().__init__(context, panel, data, object_index, total_objects, parent)

        self.labelFsk = QLabel()
        self.labelAlb = QLabel()
        self.labelKreis = QLabel()
        self.labelGemeinde = QLabel()
        self.labelGemarkung = QLabel()
        self.labelFlZaNe = QLabel()
        self.labelEntstehung = QLabel()
        self.labelBeginntEndet = QLabel()
        self.labelFlaecheAmt = QLabel()
        self.labelFlaecheKarte = QLabel()
        self.labelAlkisId = QLabel()

        self.setLayout(QFormLayout())
        self.layout().setHorizontalSpacing(64)

        self.layout().addRow("Flurstückskennzeichen:", self.labelFsk)
        self.layout().addRow("ALB:", self.labelAlb)
        self.layout().addRow("Kreis:", self.labelKreis)
        self.layout().addRow("Gemeinde:", self.labelGemeinde)
        self.layout().addRow("Gemarkung:", self.labelGemarkung)
        self.layout().addRow("Flur / Zähler / Nenner:", self.labelFlZaNe)
        self.layout().addRow("Entstehung:", self.labelEntstehung)
        self.layout().addRow("Beginnt/Endet:", self.labelBeginntEndet)
        self.layout().addRow("amtliche Fläche [m²]:", self.labelFlaecheAmt)
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
        self.data_gvStand = DialogBindingWidget()
        self.data_gvAnlass = DialogBindingWidget()
        self.data_gvEigentuemer = DialogBindingWidget()
        self.data_gvVorgaenger = DialogBindingWidget()
        self.data_gvBuchgrundstueck = DialogBindingWidget()
        self.data_gvNutzung = DialogBindingWidget()
        self.data_gvLagebezeichnung = DialogBindingWidget()
        self.data_gvDienststellen = DialogBindingWidget()
        self.data_gvBodenschaetzung = DialogBindingWidget()
        self.data_gvDienstbarkeiten = DialogBindingWidget()

        self.layout().addRow(self.data_gvStand)
        self.layout().addRow(self.data_gvAnlass)
        self.layout().addRow(self.data_gvEigentuemer)
        self.layout().addRow(self.data_gvVorgaenger)
        self.layout().addRow(self.data_gvBuchgrundstueck)
        self.layout().addRow(self.data_gvNutzung)
        self.layout().addRow(self.data_gvLagebezeichnung)
        self.layout().addRow(self.data_gvDienststellen)
        self.layout().addRow(self.data_gvBodenschaetzung)
        self.layout().addRow(self.data_gvDienstbarkeiten)

    def set_label_texts(self):
        # Flurstückskennzeichen
        self.labelFsk.setText(f"{self.get_value('fsk', '')}")
        self.labelAlb.setText(f"{self.get_value('flstalb', '')}")

        # Kreis
        self.labelKreis.setText(f"{self.get_value('gkz_krs', '')} - {self.get_value('gkz_krs_text', '')}")

        # Gemeinde
        self.labelGemeinde.setText(f"{self.get_value('gkz_gem', '')} - {self.get_value('gemeindename', '')}")

        # Gemarkung
        self.labelGemarkung.setText(f"{self.get_value('gmk_gmn', '')} - {self.get_value('gemarkungsname', '')}")

        # Flur / Zähler / Nenner
        self.labelFlZaNe.setText(
            f"{self.get_value('fln', '')}/"
            f"{self.get_value('fsn_zae', '')}/"
            f"{self.get_value('fsn_nen', '')}"
        )

        # Entstehung
        self.labelEntstehung.setText(f"{commonfunctions.test_date(self.get_value('zde', ''))}")

        # Beginnt/Endet
        self.labelBeginntEndet.setText(
            f"{commonfunctions.test_date(self.get_value('beginnt', ''))}/"
            f"{'-' if not self.get_value('endet', '') else commonfunctions.test_date(self.get_value('endet', ''))}"
        )

        # amtliche Fläche [m²]
        amtlicheflaeche = self.get_value("amtlicheflaeche", "")
        self.labelFlaecheAmt.setText(f"{commonfunctions.get_formatted_string(amtlicheflaeche, 2)}")

        # Fläche in der Karte [m²]
        area = self.get_value("area", "")
        self.labelFlaecheKarte.setText(
            f"{commonfunctions.get_formatted_string(area, 3)} "
            f"(Abweichung: "
            f"{str(commonfunctions.get_diff_in_perc(amtlicheflaeche, area, 3)).replace('.', ',')}"
            f"%)"
        )

        # Alkis-ID
        self.labelAlkisId.setText(self.get_value("id", ""))
