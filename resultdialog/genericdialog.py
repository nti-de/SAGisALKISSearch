import os
import webbrowser

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog
from qgis.PyQt import uic, QtGui

from .excelexportdialog import ExcelExportDialog
from .. import loggerutils
from .. import searchresulthandler
from .. import settings
from .. import utils
from ..resultdialog.dialogtab import DialogTab
from ..sagisgndlgconfig import sagisgndlgconfig_utils
from ..sagisgndlgconfig.configcontext import ConfigContext

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "../ui/resultdialogbase.ui"))


class GenericDialog(QDialog, FORM_CLASS):
    closed = pyqtSignal()

    def __init__(self, config_context: ConfigContext, result_list: list[dict], parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.context = config_context
        self.result_list = result_list

        if self.context.config.container.caption:
            self.setWindowTitle(self.context.config.container.caption)

        self.current_object_index = -1
        self.tabs: dict[int, DialogTab] = {}
        self.current_tab = None
        self.add_tabs()

        if self.result_list:
            self.labelIndex.setText(f"{len(self.result_list)}/{len(self.result_list)}")

        self.buttonFirst.clicked.connect(lambda: self.set_current_object(0))
        self.buttonPrevious.clicked.connect(lambda: self.set_current_object(self.current_object_index - 1))
        self.buttonNext.clicked.connect(lambda: self.set_current_object(self.current_object_index + 1))
        self.buttonLast.clicked.connect(lambda: self.set_current_object(len(self.result_list) - 1))

        self.buttonShowCurrent.clicked.connect(self.show_current_clicked)
        self.buttonShowAll.clicked.connect(self.show_all_clicked)
        self.buttonExportExcel.clicked.connect(self.export_excel_clicked)
        self.buttonClose.clicked.connect(self.close)

        if not self.context.result_layer:
            self.buttonShowCurrent.setDisabled(True)
            self.buttonShowAll.setDisabled(True)

        if not self.result_list:
            self.toolBar.setDisabled(True)

        self.sagis_web_url = settings.sagisweburl()
        self.buttonSagisweb.setVisible(self.sagis_web_url != "")
        self.buttonSagisweb.clicked.connect(self.sagisweb_clicked)

    def closeEvent(self, e: QtGui.QCloseEvent) -> None:
        super().closeEvent(e)
        self.context.datasource.close_and_remove_connection()
        self.closed.emit()

    def showEvent(self, e: QtGui.QShowEvent) -> None:
        super().showEvent(e)
        if self.result_list:
            # Fix index label size
            self.labelIndex.setFixedSize(self.labelIndex.size())
            self.set_current_object(0)

    def current_object(self) -> dict:
        return self.result_list[self.current_object_index] if self.current_object_index >= 0 else {}

    def add_tabs(self):
        for i, panel in enumerate(self.context.config.container.info_template.panels.panel):
            if not panel.active:
                continue
            tab = DialogTab(self.context, panel)
            self.tabs[i] = tab

    def set_current_object(self, object_index: int):
        if not self.result_list:
            return

        self.context.data_dicts.clear()

        object_index = 0 if object_index < 0 else len(self.result_list) - 1 if object_index > len(self.result_list) - 1 else object_index
        self.current_object_index = object_index
        self.get_base_data()
        self.update_tabs()

        self.labelIndex.setText(f"{self.current_object_index + 1}/{len(self.result_list)}")

        self.buttonFirst.setDisabled(object_index == 0)
        self.buttonPrevious.setDisabled(object_index == 0)
        self.buttonNext.setDisabled(object_index == len(self.result_list) - 1)
        self.buttonLast.setDisabled(object_index == len(self.result_list) - 1)

    def update_tabs(self):
        current_tab = self.tabWidget.currentWidget()
        self.tabWidget.clear()

        for i, tab in self.tabs.items():
            tab.update_items()
            if tab.result_count() == 0 and tab.panel.hide_if_query_is_empty:
                continue
            caption = tab.panel.caption if tab.panel.query.allow_max_results == 1 else f"{tab.panel.caption} ({tab.result_count()})"
            self.tabWidget.addTab(tab, caption)

        i = self.tabWidget.indexOf(current_tab)
        if i > -1:
            self.tabWidget.setCurrentWidget(current_tab)

    def get_base_data(self):
        if self.current_object_index < 0:
            return
        if not self.context.config.container.info_template.panels.panel:
            return

        current_object = self.result_list[self.current_object_index]
        current_object_id = utils.get_case_insensitive(current_object, self.context.primary_key_name)

        panel = self.context.config.container.info_template.panels.panel[0]
        if not panel.query.sql:
            return
        sql = sagisgndlgconfig_utils.replace_schema_placeholder(panel.query.sql, self.context.config)
        sql = sagisgndlgconfig_utils.insert_object_id(sql, current_object_id)

        data = self.context.datasource.select_into_dict_list(sql, null_value_to_none=True)
        if not data and self.context.datasource.error_text:
            loggerutils.log_error(f"Fehler (GenericDialog):\n{self.context.datasource.error_text}")
        data = data if data else []

        name = panel.query.name
        if name:
            self.context.data_dicts[name] = data

    def show_current_clicked(self):
        current = self.current_object()
        if not current or not self.context.primary_key_name:
            return
        searchresulthandler.highlight_result(self.context.result_layer, utils.get_case_insensitive(current, self.context.primary_key_name))

    def show_all_clicked(self):
        if not self.result_list or not self.context.primary_key_name:
            return
        values = [utils.get_case_insensitive(r, self.context.primary_key_name) for r in self.result_list]
        searchresulthandler.highlight_result(self.context.result_layer, values)

    def export_excel_clicked(self):
        object_ids = [utils.get_case_insensitive(r, self.context.primary_key_name) for r in self.result_list]
        if not object_ids:
            return

        dlg = ExcelExportDialog(
            self.context.class_name,
            object_ids,
            self.current_object_index,
            self.context.datasource,
            self.context.primary_key_name,
            self
        )
        dlg.setModal(True)
        dlg.show()
        dlg.exec_()

    def sagisweb_clicked(self):
        current_object_pk_value = utils.get_case_insensitive(self.current_object(), self.context.primary_key_name)
        url = f"{self.sagis_web_url.rstrip('/')}/Services/Widgets/SAGisNotify/SAGisNotify.aspx?classname={self.context.class_name}&propertyname={self.context.primary_key_name}&keys={current_object_pk_value}"
        try:
            webbrowser.open(url)
        except Exception as e:
            loggerutils.log_error(f"Fehler (GenericDialog):\n{str(e)}")
