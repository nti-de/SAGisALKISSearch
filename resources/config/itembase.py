from abc import ABC, abstractmethod
from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlQueryModel
from PyQt5.QtWidgets import QFrame, QTableView

from ... import commonfunctions
from ... import loggerutils
from ...sagisgndlgconfig import sagisgndlgconfig_utils
from ...sagisgndlgconfig.configcontext import ConfigContext
from ...sagisgndlgconfig.sagis_gn_dlg_config import SagisGnDlgConfig


class ItemBase(QFrame):
    """DEPRECATED"""

    __metaclass__ = ABC

    def __init__(self, context: ConfigContext,
                 panel: SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel,
                 data: dict, object_index=-1, total_objects=0, parent=None):
        super().__init__(parent)
        self.context = context
        self.panel = panel
        self.data = data
        self.object_index = object_index
        self.total_objects = total_objects

        self.set_index(self.object_index, self.total_objects)

    @abstractmethod
    def set_label_texts(self, data: dict):
        pass

    def set_index(self, current: int, total: int):
        return

    def get_value(self, key: str, default="") -> Any:
        value = self.data.get(key, default)
        return value if value else default

    def bind_tableviews(self):
        for binding in self.panel.bindings:
            self.add_binding(binding)

    def add_binding(self, binding: SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel.Bindings):
        db = self.context.datasource.database

        if not db or not binding.sql:
            return

        bind_to = binding.bind_to
        if not bind_to:
            return
        table_view: QTableView = self.findChild(QTableView, bind_to)
        if not table_view:
            return

        table_view.verticalHeader().setVisible(False)

        if not db.isOpen():
            db.open()

        sql = sagisgndlgconfig_utils.replace_schema_placeholder(binding.sql, self.context.config)
        success, sql = commonfunctions.insert_dict_values_into_string(sql, self.data)
        if not success:
            loggerutils.log_error(f"Fehler (ItemBase):\nAbfrageergebnis enthält nicht '{sql}'")
            return

        model = QSqlQueryModel()
        model.setQuery(sql, db)
        table_view.setModel(model)

        # Change header text
        header_dict = {header_text.from_value: header_text.to for header_text in binding.header_text}

        for c in range(model.columnCount()):
            old_text = model.headerData(c, Qt.Horizontal, Qt.DisplayRole)
            if old_text in header_dict:
                model.setHeaderData(c, Qt.Horizontal, header_dict.get(old_text), Qt.DisplayRole)
