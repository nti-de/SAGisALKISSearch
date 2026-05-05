import os
import re
from typing import Optional

from qgis.PyQt.QtCore import Qt, QTimer
from qgis.PyQt.QtGui import QIntValidator
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from qgis.PyQt import uic, QtGui
from qgis.core import Qgis, QgsApplication, QgsProject, QgsVectorLayer
from qgis.utils import iface

from . import loggerutils
from . import searchresulthandler
from . import settings
from . import utils
from .alkisdatasources.alkisdatasource import AlkisDataSource, AlkisDataSourceType
from .constants import PROJECT_ENTRY_SCOPE
from .resultdialogbuilder import ResultDialogBuilder
from .tasks.flurstuecksearchtask import FlurstueckSearchTask
from .ui.extendedcombobox import ExtendedComboBox
from .ui.taskprogressbar import TaskProgressBar

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

        self.search_button = self.buttonBox.addButton("Suchen", QDialogButtonBox.ButtonRole.ActionRole)
        self.search_button.clicked.connect(self.search_clicked)

        self.open_dialog_button = self.buttonBox.addButton("Dialog öffnen", QDialogButtonBox.ButtonRole.ActionRole)
        self.open_dialog_button.clicked.connect(self.open_dialog_clicked)

        self.unselect_button = self.buttonBox.addButton("Markierungen aufheben", QDialogButtonBox.ButtonRole.ActionRole)
        self.unselect_button.setVisible(False)
        self.unselect_button.clicked.connect(searchresulthandler.unselect_flurstuecke)

        self.task_progress_bar = TaskProgressBar(self)
        self.task_progress_bar.task_started.connect(self._on_task_started)
        self.task_progress_bar.task_finished.connect(self._on_task_finished)
        self.layout().addWidget(self.task_progress_bar, 1, 0)

        self.result_list_widget: Optional[QListWidget] = None

        self.datasource: Optional[AlkisDataSource] = None
        self.last_connection_name = settings.connection()
        self.last_database_type = settings.datasourcetype()
        self.set_database(settings.datasourcetype())

        self.cbMunicipality.currentIndexChanged.connect(self.populate_streets)
        self.cbStreet.currentIndexChanged.connect(self.populate_numbers)

        self.tab_changed(self.tabWidget.currentIndex())
        self.tabWidget.currentChanged.connect(self.tab_changed)

        self.search_task: Optional[FlurstueckSearchTask] = None

    def showEvent(self, e: QtGui.QShowEvent) -> None:
        super().showEvent(e)
        if settings.datasourcetype() != self.last_database_type or settings.connection() != self.last_connection_name:
            self.set_database(settings.datasourcetype())
        self.check_datasource_types()

    def reject(self):
        if self.search_task and self.search_task.isActive():
            self.search_task.cancel()
        super().reject()

    def set_database(self, datasource_type: Optional[AlkisDataSourceType]):
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

        if not self.datasource or not self.datasource.connection or not self.datasource.connection_success:
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

        project_database_type, ok = QgsProject.instance().readEntry(PROJECT_ENTRY_SCOPE, "datasourcetype")
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

        if not self.datasource:
            return

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

        if not self.datasource:
            return

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

        if not self.datasource:
            return

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

        if not self.datasource:
            return

        street_key = self.cbStreet.currentData()
        if not street_key:
            self.cbNumber.setEnabled(False)
            return

        self.cbNumber.setEnabled(True)
        numbers = self.datasource.get_numbers(street_key)
        if not numbers:
            return

        sorted_numbers = sorted(numbers, key=self.house_number_key)

        self.cbNumber.addItem("", None)
        for number in sorted_numbers:
            value = utils.get_case_insensitive(number, "value")
            key = utils.get_case_insensitive(number, "key")
            self.cbNumber.addItem(value, key)

    @staticmethod
    def house_number_key(item):
        value = utils.get_case_insensitive(item, "value").strip()
        match = re.match(r'(\d+)\s*([A-Za-z]*)', value)

        if not match:
            return float('inf'), value  # push invalid entries to the end

        number = int(match.group(1))
        suffix = match.group(2).casefold() if match.group(2) else ''

        return number, suffix

    def populate_gemarkung(self):
        self.cbGemarkung.clear()

        if not self.datasource:
            return

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
        if not self.datasource:
            return

        fsk = self.leFsk.text()
        gmk_gmn = self.cbGemarkung.currentData()
        fln = self.leFln.text()
        fsn_zae = self.leFsnZae.text()
        fsn_nen = self.leFsnNen.text()

        self.search_task = FlurstueckSearchTask(
            self.datasource, fsk=fsk, gmk_gmn=gmk_gmn, fln=fln, fsn_zae=fsn_zae, fsn_nen=fsn_nen)
        self.search_task.taskCompleted.connect(self.flurstueck_search_task_completed)
        self.search_task.taskTerminated.connect(self.flurstueck_search_task_terminated)
        task_id = QgsApplication.taskManager().addTask(self.search_task)
        self.task_progress_bar.track(task_id)

    def flurstueck_search_task_completed(self):
        if not self.search_task:
            return
        self.flurstueck_results = self.search_task.results
        self.search_task = None

        layer_id, ok = QgsProject.instance().readEntry(PROJECT_ENTRY_SCOPE, "flurstueck_result_layer")
        layer = QgsProject.instance().mapLayer(layer_id) if ok else None

        self._start_list_population(layer)

    def flurstueck_search_task_terminated(self):
        self.search_task = None

    def _start_list_population(self, layer: Optional[QgsVectorLayer]) -> None:
        self.result_list_widget = QListWidget()
        self.result_list_widget.setUniformItemSizes(True)

        if layer:
            self.result_list_widget.itemClicked.connect(
                lambda item: self._on_list_item_clicked(layer, item)
            )

        results_count = len(self.flurstueck_results)
        self.task_progress_bar.begin_manual(results_count)
        self._populate_list_chunked(
            on_done=lambda: self._on_list_populated(results_count, layer)
        )

    def _populate_list_chunked(self, offset: int = 0, chunk_size: int = 100, on_done=None) -> None:
        chunk = self.flurstueck_results[offset:offset + chunk_size]
        if not chunk:
            self.task_progress_bar.end_manual()
            if on_done:
                on_done()
            return

        results_count = len(self.flurstueck_results)
        tooltip = "Suchergebnis in der Karte zeigen."
        self.result_list_widget.setUpdatesEnabled(False)
        try:
            for r in chunk:
                caption = utils.get_case_insensitive(r, "caption", "-")
                fid = utils.get_case_insensitive(r, "fid")
                item = QListWidgetItem(caption)
                item.setData(Qt.ItemDataRole.UserRole, fid)
                item.setToolTip(tooltip)
                self.result_list_widget.addItem(item)
        finally:
            self.result_list_widget.setUpdatesEnabled(True)

        next_offset = offset + chunk_size
        self.task_progress_bar.update_manual(min(next_offset, results_count))

        if next_offset < results_count:
            QTimer.singleShot(0, lambda: self._populate_list_chunked(next_offset, chunk_size, on_done))
        else:
            self.task_progress_bar.end_manual()
            if on_done:
                on_done()

    def _on_list_populated(self, result_count: int, layer: Optional[QgsVectorLayer]) -> None:
        self.tabWidget.removeTab(3)

        tab_page = QWidget()
        index = self.tabWidget.addTab(tab_page, "Ergebnisse")
        layout = QVBoxLayout()
        tab_page.setLayout(layout)
        count_label = QLabel(
            f"Ihre Suche lieferte {result_count if result_count > 0 else 'keine'} Ergebnis{'se' if result_count != 1 else ''}."
        )
        layout.addWidget(count_label)
        layout.addWidget(self.result_list_widget)

        self.open_dialog_button.setEnabled(result_count > 0)
        self.unselect_button.setEnabled(result_count > 0)
        self.tabWidget.setCurrentIndex(index)

        # Select
        p_key_values = [utils.get_case_insensitive(r, "fid") for r in self.flurstueck_results]
        searchresulthandler.flurstueck_search(layer, p_key_values)

    @staticmethod
    def _on_list_item_clicked(layer: QgsVectorLayer, item: QListWidgetItem):
        searchresulthandler.highlight_result(layer, item.data(Qt.ItemDataRole.UserRole))

    def tab_changed(self, index: int):
        self.search_button.setVisible(index <= 2)
        self.unselect_button.setVisible(index == 3)
        self.open_dialog_button.setVisible(index == 3)

    def open_dialog_clicked(self):
        if not self.datasource:
            loggerutils.log_error(f"Fehler: Keine Datenquelle gesetzt")
            return

        if not self.datasource.connection_success:
            loggerutils.log_error(f"Datenbankfehler:\n{self.datasource.error_text}")
            return

        index = 0
        if self.result_list_widget and self.result_list_widget.currentRow() >= 0:
            index = self.result_list_widget.currentRow()

        dlg_builder = ResultDialogBuilder(
            self.flurstueck_results,
            self.datasource.f_class_name,
            self.datasource.flurstueck_primary_key,
            self.datasource,
            self.datasource.config_file,
            current_index=index
        )
        dlg_builder.build()

    def _on_task_started(self) -> None:
        self.tabWidget.setEnabled(False)
        self.search_button.setEnabled(False)
        self.unselect_button.setEnabled(False)
        self.open_dialog_button.setEnabled(False)
        self.setCursor(Qt.CursorShape.WaitCursor)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Close).setCursor(Qt.CursorShape.ArrowCursor)

    def _on_task_finished(self) -> None:
        self.tabWidget.setEnabled(True)
        self.search_button.setEnabled(True)
        self.unselect_button.setEnabled(True)
        self.open_dialog_button.setEnabled(True)
        self.unsetCursor()
        self.buttonBox.button(QDialogButtonBox.StandardButton.Close).unsetCursor()
