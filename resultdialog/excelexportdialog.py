import glob
import os
import pathlib
import sys

from PyQt5.QtCore import QUrl, QDir, Qt
from PyQt5.QtGui import QStandardItem, QIcon
from qgis.core import Qgis, QgsApplication, QgsProject, QgsTask
from qgis.utils import iface

from .. import loggerutils
from ..datasources.datasource import DataSource
from ..sagisexcelexportdefinition.excelexportcontext import ExcelExportContext
from ..sagisexcelexportdefinition.excelexporttask import ExcelExportTask
from ..sagisexcelexportdefinition.sagis_excel_export_definition import *
from ..ui.twolistselection import TwoListSelection

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QRadioButton, QButtonGroup, QPushButton, \
    QFileDialog, QWidget


class ExcelExportDialog(QDialog):
    CONFIG_PATH = "resources/config/Export"

    def __init__(self, class_name: str, object_ids: list[int], current_index: int,
                 datasource: DataSource, primary_key_name: str, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "../resources/SAGis_Logo_Excel_Export.png")))

        self.class_name = class_name
        self.object_ids = object_ids
        self.current_index = current_index
        self.datasource = datasource
        self.primary_key_name = primary_key_name
        self.column_names = self.get_column_names()

        self.setStyleSheet("QWidget { font-size: 8pt }")
        self.setWindowTitle("SAGis Excel Export")

        # Reports
        self.label_reports = QLabel("Exportvorlage")
        self.label_reports.setFixedHeight(13)
        self.combo_box_reports = QComboBox()

        # Columns
        self.two_list_selection = TwoListSelection(
            left_list=sorted(self.column_names, key=str.casefold),
            left_caption="Alle Felder:",
            right_caption="Exportierte Felder:",
            clone=True,
            allow_filtering=True
        )
        self.two_list_selection.right_list_changed.connect(self.populate_sort_order)

        # Sort order
        self.label_sort_order = QLabel("Sortierreihenfolge")
        self.label_sort_order.setFixedHeight(13)
        self.combo_box_sort_order = QComboBox()
        self.populate_sort_order(self.two_list_selection.get_right_dict())

        # Current or all
        self.radio_button_current = QRadioButton(f"Für den aktuell angezeigten Datensatz ({self.current_index + 1}/{len(object_ids)})")
        self.radio_button_all = QRadioButton(f"Für alle Datensätze der aktuellen Auswahl ({len(object_ids)})")
        self.button_create = QPushButton("Erstellen")
        self.button_close = QPushButton("Schließen")

        self.button_group = QButtonGroup()
        self.button_group.addButton(self.radio_button_current)
        self.button_group.addButton(self.radio_button_all)
        self.radio_button_current.setChecked(True)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.label_reports)
        self.layout().addWidget(self.combo_box_reports)
        self.layout().addWidget(self.two_list_selection)
        self.layout().addWidget(self.label_sort_order)
        self.layout().addWidget(self.combo_box_sort_order)
        self.layout().addWidget(self.radio_button_current)
        self.layout().addWidget(self.radio_button_all)
        self.layout().addWidget(self.button_create)
        self.layout().addWidget(self.button_close)

        # Let added widgets keep their height
        self.filler_widget = QWidget()
        self.layout().addWidget(self.filler_widget)

        self.combo_box_reports.currentIndexChanged.connect(self.selected_report_changed)
        self.button_close.clicked.connect(self.close)
        self.button_create.clicked.connect(self.button_create_clicked)

        self.configs = []

        self.read_configs()
        self.populate_reports()

        self.file_path = ""
        self.task: Optional[ExcelExportTask] = None

    def read_configs(self):
        try:
            directory = os.path.join(pathlib.Path(__file__).parent.parent, pathlib.Path(self.CONFIG_PATH).__str__(), "*.xml")
            file_list = glob.glob(directory)
        except Exception as e:
            loggerutils.log_error(f"Fehler beim Lesen der Konfigurationsdateien:\n{str(e)}")
            return

        # Import XmlParser
        from xsdata.formats.dataclass.parsers import XmlParser

        for file in file_list:
            try:
                xml = pathlib.Path(file).read_text()
                parser = XmlParser()
                config = parser.from_string(xml, SagisExcelExportDefinition)
                if config.sagis_excel_export_item.feature_class.lower() == self.class_name.lower():
                    # Skip if provider restriction is set but not satisfied.
                    if config.sagis_excel_export_item.provider_type_restrictions\
                        and config.sagis_excel_export_item.provider_type_restrictions.type\
                        and self.datasource.feature_source_provider_type.lower()\
                            not in [t.lower() for t in config.sagis_excel_export_item.provider_type_restrictions.type]:
                        continue

                    self.configs.append(config)
            except Exception as e:
                loggerutils.log_error(f"Fehler beim Lesen der Konfigurationsdateien:\n{str(e)}")
                return

    def populate_reports(self):
        self.combo_box_reports.clear()
        for config in self.configs:
            self.combo_box_reports.addItem(config.sagis_excel_export_item.title, config)

        report_count = self.combo_box_reports.count()
        if report_count > 0:
            self.combo_box_reports.addItem("_" * 50)
            item: QStandardItem = self.combo_box_reports.model().item(report_count)
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
        self.combo_box_reports.addItem("Datenexport - Gesamter Datensatz", -1)

    def populate_sort_order(self, items: dict):
        self.combo_box_sort_order.clear()
        self.combo_box_sort_order.addItem("")
        if items:
            self.combo_box_sort_order.addItems(sorted(list(items.keys())))
        else:
            self.combo_box_sort_order.addItems(sorted(self.column_names))

    def selected_report_changed(self, _: int):
        report = self.combo_box_reports.currentData()

        self.two_list_selection.setVisible(report == -1)
        self.label_sort_order.setVisible(report == -1)
        self.combo_box_sort_order.setVisible(report == -1)

        if self.two_list_selection.isVisible():
            self.resize(max(self.width(), 732), max(self.height(), 515))

    def get_column_names(self) -> list[str]:
        column_names = self.datasource.get_column_names(self.class_name.lower())
        return column_names

    def button_create_clicked(self):
        if self.task and self.task.status() == QgsTask.TaskStatus.Running:
            self.task.cancel()
        else:
            config = self.combo_box_reports.currentData()
            if not config:
                return
            if isinstance(config, SagisExcelExportDefinition):
                self.create_export_with_config(config)
            elif config == -1:
                self.create_generic_export()

    def get_save_file_name(self, default_name: str):
        default_path = QgsProject.instance().absolutePath() or os.getcwd()
        self.file_path = QFileDialog.getSaveFileName(
            self,
            "Speichern unter",
            os.path.join(default_path, default_name),
            "Excel-Arbeitsmappe (*.xlsx)"
        )[0]

    def create_export_with_config(self, config: SagisExcelExportDefinition):
        default_name = config.sagis_excel_export_item.file_name or config.sagis_excel_export_item.feature_class
        self.get_save_file_name(default_name)
        if not self.file_path:
            return

        if self.radio_button_current.isChecked():
            ids = [self.object_ids[self.current_index]]
        else:
            ids = self.object_ids

        if not ids:
            loggerutils.log_error("Fehler:\nKeine zu exportierenden Objekt-IDs")
            return

        context = ExcelExportContext(
            config=config,
            datasource=self.datasource,
            primary_key_name=self.primary_key_name,
            object_ids=ids,
            file_path=self.file_path
        )

        self.task = ExcelExportTask(context)
        self.task.taskCompleted.connect(self.task_completed)
        self.task.taskTerminated.connect(self.task_completed)
        QgsApplication.taskManager().addTask(self.task)

        self.button_create.setText("Abbrechen")
        self.button_close.setDisabled(True)

    def create_generic_export(self):
        """Builds and uses SagisExcelExportDefinition."""

        selected_columns = (self.two_list_selection.get_right_dict().keys())
        sql = self.datasource.get_generic_select_statement(self.class_name, selected_columns)
        sql += f" WHERE {self.primary_key_name} = {{0}}"

        order_column = self.combo_box_sort_order.currentText()

        worksheet = SagisWorksheetType(
            tab_color="blue",
            work_sheet_name=f"Arbeitsblatt Export",
            sql=sql,
            order_by=order_column if order_column else None
        )

        export_item = SagisExcelExportItemType(
            feature_class=self.class_name.lower(),
            work_sheet=[worksheet]
        )

        config = SagisExcelExportDefinition(sagis_excel_export_item=export_item)
        self.create_export_with_config(config)

    def task_completed(self):
        if self.task.status() == QgsTask.TaskStatus.Complete:
            iface.messageBar().pushMessage(
                title="Excel Export erfolgreich",
                text=f"<a href='{QUrl.fromLocalFile(str(pathlib.Path(self.file_path).parent)).toString()}'>{QDir.toNativeSeparators(self.file_path)}</a>",
                level=Qgis.MessageLevel.Success,
                duration=0
            )
        elif self.task.error:
            error = self.task.error
            loggerutils.log_error(f"Fehler:\n{str(error)}")

        self.task = None
        self.button_create.setText("Erstellen")
        self.button_close.setEnabled(True)
