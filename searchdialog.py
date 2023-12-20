import os
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QListWidgetItem, QWidget, QVBoxLayout, QLabel, QListWidget
from qgis.PyQt import uic, QtGui
from qgis.core import Qgis, QgsProject, QgsVectorLayer
from qgis.utils import iface

from . import loggerutils
from . import searchresulthandler
from . import settings
from . import utils
from .alkisdatasources.alkisdatasource import AlkisDataSource, AlkisDataSourceType
from .resultdialogbuilder import ResultDialogBuilder
from .ui.extendedcombobox import ExtendedComboBox

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "ui/search.ui"))
SGBMEBL = {
    "01": "Schleswig-Holstein",
    "02": "Hamburg",
    "03": "Niedersachsen",
    "04": "Bremen",
    "05": "Nordrhein-Westfalen",
    "06": "Hessen",
    "07": "Rheinland-Pfalz",
    "08": "Baden-Württemberg",
    "09": "Bayern",
    "10": "Saarland",
    "11": "Berlin",
    "12": "Brandenburg",
    "13": "Mecklenburg-Vorpommern",
    "14": "Sachsen",
    "15": "Sachsen-Anhalt",
    "16": "Thüringen"
}


class SearchDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.flurstueck_results: list[dict] = []

        # Street search
        self.tab0 = self.tabWidget.widget(0)
        self.cbName = ExtendedComboBox()
        self.tab0.layout().addRow("Name:", self.cbName)

        # Building number search
        self.tab1 = self.tabWidget.widget(1)
        self.cbMunicipality = ExtendedComboBox()
        self.cbStreet = ExtendedComboBox()
        self.cbNumber = ExtendedComboBox()
        self.cbStreet.setDisabled(True)
        self.cbNumber.setDisabled(True)
        self.tab1.layout().addRow("Gemeinde:", self.cbMunicipality)
        self.tab1.layout().addRow("Straße:", self.cbStreet)
        self.tab1.layout().addRow("Hausnummer:", self.cbNumber)

        # Flurstück search
        self.tab2 = self.tabWidget.widget(2)
        self.cbGemarkung = ExtendedComboBox()
        self.tab2.layout().insertRow(3, "Gemarkung:", self.cbGemarkung)
        self.leFsk.textChanged.connect(self.fsk_changed)
        validator = QIntValidator(self)
        self.leFln.setValidator(validator)
        self.leFsnZae.setValidator(validator)
        self.leFsnNen.setValidator(validator)

        self.search_button = self.buttonBox.addButton("Suchen", QDialogButtonBox.ActionRole)
        self.search_button.clicked.connect(self.search_clicked)

        self.open_dialog_button = self.buttonBox.addButton("Dialog öffnen", QDialogButtonBox.ActionRole)
        self.open_dialog_button.clicked.connect(self.open_dialog_clicked)

        self.unselect_button = self.buttonBox.addButton("Markierungen aufheben", QDialogButtonBox.ActionRole)
        self.unselect_button.setVisible(False)
        self.unselect_button.clicked.connect(searchresulthandler.unselect_flurstuecke)

        self.rejected.connect(self.close_database)

        self.datasource: Optional[AlkisDataSource] = None
        self.last_connection_name = settings.connection()
        self.last_database_type = settings.datasourcetype()
        self.set_database(settings.datasourcetype())

        self.cbMunicipality.currentIndexChanged.connect(self.populate_streets)
        self.cbStreet.currentIndexChanged.connect(self.populate_numbers)

        self.tab_changed(self.tabWidget.currentIndex())
        self.tabWidget.currentChanged.connect(self.tab_changed)

    def showEvent(self, e: QtGui.QShowEvent) -> None:
        super().showEvent(e)
        if settings.datasourcetype() != self.last_database_type or settings.connection() != self.last_connection_name:
            self.set_database(settings.datasourcetype())
        self.check_datasource_types()

    def closeEvent(self, e: QtGui.QCloseEvent) -> None:
        super().closeEvent(e)
        self.close_database()

    def close_database(self):
        if self.datasource.database:
            self.datasource.database.close()

    def set_database(self, datasource_type: AlkisDataSourceType):
        self.datasource = None

        # Reset dialog
        self.cbName.clear()
        self.cbMunicipality.clear()
        self.cbStreet.clear()
        self.cbNumber.clear()
        self.cbGemarkung.clear()
        self.labelBundesland.clear()
        self.leFsk.clear()
        self.leFln.clear()
        self.leFsnZae.clear()
        self.leFsnNen.clear()
        self.tabWidget.removeTab(3)

        self.datasource = utils.create_datasource()

        if not self.datasource or not self.datasource.database or not self.datasource.connection_success:
            message = "Datenbankfehler:\nDatenbankverbindung fehlgeschlagen"
            message += f" -> {self.datasource.error_text}" if self.datasource.error_text else ""
            loggerutils.log_error(message)
            return

        self.last_database_type = datasource_type
        self.last_connection_name = settings.connection()

        self.populate_names()
        self.populate_municipalities()
        self.populate_gemarkung()
        self.set_bundesland()

    @staticmethod
    def check_datasource_types() -> bool:
        """Returns True if datasource types from settings and project match or if no type is saved in the project,
        Returns False otherwise.
        """

        project_database_type, ok = QgsProject.instance().readEntry("sagis_alkis_search", "datasourcetype")
        if not ok or not settings.datasourcetype() or project_database_type == settings.datasourcetype().value:
            return True
        message = f"Eingestellter Datenbanktyp ('{settings.datasourcetype().value}') stimmt nicht mit dem im Projekt gespeicherten ('{project_database_type}') überein"
        loggerutils.log_error(message)
        iface.messageBar().pushMessage(
            title="SAGis ALKIS Suche",
            text=message,
            level=Qgis.MessageLevel.Warning,
            duration=5
        )
        return False

    def set_bundesland(self):
        bl_id = self.datasource.get_bundesland()

        if isinstance(bl_id, int):
            bl_id = f"{bl_id:02d}"
        self.labelBundesland.setText(f"{bl_id} - {SGBMEBL.get(bl_id, '')}")

    def populate_names(self):
        self.cbName.clear()

        streets = self.datasource.get_streetnames()
        self.cbName.setToolTip(f"{len(streets)} Datensätze" if len(streets) != 1 else "1 Datensatz")
        if not streets:
            return

        self.cbName.addItem("", None)
        for street in streets:
            label_text = utils.get_case_insensitive(street, "label_text")
            fid = utils.get_case_insensitive(street, "fid")
            self.cbName.addItem(label_text, fid)

    def populate_municipalities(self):
        self.cbMunicipality.clear()

        municipalities = self.datasource.get_municipalities()
        if not municipalities:
            return

        self.cbMunicipality.addItem("", None)
        for municipality in municipalities:
            value = utils.get_case_insensitive(municipality, "value")
            key = utils.get_case_insensitive(municipality, "key")
            self.cbMunicipality.addItem(value, key)

    def populate_streets(self):
        self.cbStreet.clear()

        municipality_id = self.cbMunicipality.currentData()
        if not municipality_id:
            self.cbStreet.setEnabled(False)
            return

        self.cbStreet.setEnabled(True)
        streets = self.datasource.get_streets(municipality_id)
        if not streets:
            return

        self.cbStreet.addItem("", None)
        for street in streets:
            value = utils.get_case_insensitive(street, "value")
            key = utils.get_case_insensitive(street, "key")
            self.cbStreet.addItem(value, key)

    def populate_numbers(self):
        self.cbNumber.clear()

        street_key = self.cbStreet.currentData()
        if not street_key:
            self.cbNumber.setEnabled(False)
            return

        self.cbNumber.setEnabled(True)
        numbers = self.datasource.get_numbers(street_key)
        if not numbers:
            return

        self.cbNumber.addItem("", None)
        for number in numbers:
            value = utils.get_case_insensitive(number, "value")
            key = utils.get_case_insensitive(number, "key")
            self.cbNumber.addItem(value, key)

    def populate_gemarkung(self):
        self.cbGemarkung.clear()

        gemarkungen = self.datasource.get_gemarkungen()
        if not gemarkungen:
            return

        self.cbGemarkung.addItem("", None)
        for gemarkung in gemarkungen:
            name = utils.get_case_insensitive(gemarkung, "bezeichnung")
            key = utils.get_case_insensitive(gemarkung, "schluessel")
            self.cbGemarkung.addItem(f"{name} ({key})", key)

    def fsk_changed(self, text: str):
        fsk_set = True if text else False
        self.cbGemarkung.setDisabled(fsk_set)
        self.leFln.setDisabled(fsk_set)
        self.leFsnZae.setDisabled(fsk_set)
        self.leFsnNen.setDisabled(fsk_set)

    def search_clicked(self):
        if self.tabWidget.currentIndex() == 0:
            self.search_street()
        elif self.tabWidget.currentIndex() == 1:
            self.search_house_number()
        elif self.tabWidget.currentIndex() == 2:
            self.search_flurstueck()

    def search_street(self):
        if not self.check_datasource_types():
            return
        value = self.cbName.currentData()
        if not value:
            return
        searchresulthandler.street_search(value)

    def search_house_number(self):
        if not self.check_datasource_types():
            return
        value = self.cbNumber.currentData()
        if not value:
            return
        searchresulthandler.building_search(value)

    def search_flurstueck(self):
        fsk = self.leFsk.text()
        gmk_gmn = self.cbGemarkung.currentData()
        fln = self.leFln.text()
        fsn_zae = self.leFsnZae.text()
        fsn_nen = self.leFsnNen.text()

        self.flurstueck_results = self.datasource.search_flurstuecke(fsk=fsk, gmk_gmn=gmk_gmn, fln=fln, fsn_zae=fsn_zae, fsn_nen=fsn_nen)

        p_key_values = [utils.get_case_insensitive(r, "fid") for r in self.flurstueck_results]
        layer = searchresulthandler.flurstueck_search(p_key_values)

        self.create_result_tab(self.flurstueck_results, layer)

    def create_result_tab(self, results: list[dict], layer: QgsVectorLayer):
        self.tabWidget.removeTab(3)

        tab_page = QWidget()
        index = self.tabWidget.addTab(tab_page, "Ergebnisse")
        layout = QVBoxLayout()
        tab_page.setLayout(layout)
        count_label = QLabel(
            f"Ihre Suche lieferte {len(results) if len(results) > 0 else 'keine'} Ergebnis{'se' if len(results) != 1 else ''}."
        )
        list_widget = QListWidget()
        layout.addWidget(count_label)
        layout.addWidget(list_widget)

        for r in results:
            caption = utils.get_case_insensitive(r, "caption", "-")
            fid = utils.get_case_insensitive(r, "fid")
            item = QListWidgetItem(caption, list_widget)
            item.setData(Qt.UserRole, fid)
            item.setToolTip("Suchergebnis in der Karte zeigen.")
        if layer:
            list_widget.itemClicked.connect(lambda i: searchresulthandler.highlight_result(layer, i.data(Qt.UserRole)))

        self.open_dialog_button.setEnabled(len(results) > 0)
        self.unselect_button.setEnabled(len(results) > 0)
        self.tabWidget.setCurrentIndex(index)

    def tab_changed(self, index: int):
        self.search_button.setVisible(index <= 2)
        self.unselect_button.setVisible(index >= 2)
        self.open_dialog_button.setVisible(index > 2)

    def open_dialog_clicked(self):
        if not self.datasource.connection_success:
            loggerutils.log_error(f"Datenbankfehler:\n{self.datasource.error_text}")
            return
        dlg_builder = ResultDialogBuilder(
            self.flurstueck_results,
            self.datasource.f_class_name,
            self.datasource.flurstueck_primary_key,
            self.datasource,
            self.datasource.config_file
        )
        dlg_builder.build()
