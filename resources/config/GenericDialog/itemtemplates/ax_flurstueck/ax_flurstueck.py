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
        self.labelRechtesbehelfsVerfahren = QLabel()
        self.labelFlurstueckFolge = QLabel()
        self.labelAbweichenderRechtszustand = QLabel()
        self.labelZustaendigeStelle = QLabel()
        self.labelFlurstueckNachweis = QLabel()
        self.labelAnlass1 = QLabel()
        self.labelAnlass2 = QLabel()
        # self.labelBuchungsstelle = QLabel()
        # self.labelFid = QLabel()
        self.labelAlkisId = QLabel()
        # self.labelLetzteAusleitung = QLabel()

        self.setLayout(QFormLayout())
        self.layout().setHorizontalSpacing(64)

        self.layout().addRow("Gemeindezugehörigkeit:", self.labelGemeindeZugehoerigkeit)
        self.layout().addRow("Gemarkung:", self.labelGemarkung)
        self.layout().addRow("Flur / Zähler / Nenner:", self.labelFlurZaehlerNenner)
        self.layout().addRow("Flurstückskennzeichen:", self.labelFlurstueckKennzeichen)
        self.layout().addRow("Flurstücksfolge:", self.labelFlurstueckFolge)
        self.layout().addRow("zuständige Stelle:", self.labelZustaendigeStelle)
        self.layout().addRow("Anlass1:", self.labelAnlass1)
        self.layout().addRow("Anlass2:", self.labelAnlass2)
        self.layout().addRow("Entstehung:", self.labelEntstehung)
        self.layout().addRow("amtliche Fläche [m²]:", self.labelamtlicheFlaeche)
        self.layout().addRow("Fläche in der Karte [m²]:", self.labelFlaecheKarte)
        self.layout().addRow("Rechtsbehelfsverfahren:", self.labelRechtesbehelfsVerfahren)
        self.layout().addRow("abweichender Rechtszustand:", self.labelAbweichenderRechtszustand)
        self.layout().addRow("zweifelhafter Flurstücksnachweis:", self.labelFlurstueckNachweis)
        # self.layout().addRow("Buchungsstelle:", self.labelBuchungsstelle)
        # self.layout().addRow("FID:", self.labelFid)
        self.layout().addRow("Alkis-ID:", self.labelAlkisId)
        # self.layout().addRow("Letzte Ausleitung:", self.labelLetzteAusleitung)

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
        self.dataV_LetzteAusleitung = DialogBindingWidget()
        self.dataV_EIGENTUEMER_DIST_OVERVIEW = DialogBindingWidget()
        self.dataAX_HISTORISCHESFST = DialogBindingWidget()

        self.layout().addRow(self.dataV_LetzteAusleitung)
        self.layout().addRow(self.dataV_EIGENTUEMER_DIST_OVERVIEW)
        self.layout().addRow(self.dataAX_HISTORISCHESFST)

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

        amtlicheflaeche = self.get_value('amtlicheflaeche')
        self.labelamtlicheFlaeche.setText(
            f"{commonfunctions.get_formatted_string(amtlicheflaeche)}"
        )

        self.labelFlurZaehlerNenner.setText(
            f"{self.get_value('flurnummer')}/{self.get_value('flurstuecksnummer_zaehler')}/{self.get_value('flurstuecksnummer_nenner')}"
        )

        area = self.get_value('area')
        self.labelFlaecheKarte.setText(
            f"{commonfunctions.get_formatted_string(area)} "
            f"(Abweichung: {str(commonfunctions.get_diff_in_perc(amtlicheflaeche, area, 2)).replace('.', ',')}%)"
        )

        self.labelFlurstueckKennzeichen.setText(
            f"{self.get_value('flurstueckskennzeichen')}"
        )

        self.labelRechtesbehelfsVerfahren.setText(
            f"{self.get_value('xrechtsbehelfsverfahren')}"
        )

        self.labelFlurstueckFolge.setText(
            f"{self.get_value('flurstuecksfolge')}"
        )

        self.labelAbweichenderRechtszustand.setText(
            f"{self.get_value('xabweichenderrechtszustand')}"
        )

        self.labelZustaendigeStelle.setText(
            f"{self.get_value('zustaendigestelle')}/{self.get_value('zustaendigestellebez')}"
        )

        self.labelFlurstueckNachweis.setText(
            f"{self.get_value('xzweifelhafterflurstuecksna')}"
        )

        self.labelAnlass1.setText(
            f"{self.get_value('anlass1')} - {self.get_value('anlass1_value')}"
        )

        self.labelAnlass2.setText(
            f"{self.get_value('anlass2')} - {self.get_value('anlass2_value')}"
        )

        # self.labelBuchungsstelle.setText("")

        # self.labelFid.setText(
        #     f"{self.get_value('fid')}"
        # )

        self.labelAlkisId.setText(
            f"{self.get_value('id')}"
        )

        # self.labelLetzteAusleitung.setText("")
