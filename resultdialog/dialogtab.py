from typing import Union

from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout

from .dialogitem import DialogItem
from .. import commonfunctions
from .. import loggerutils
from ..sagisgndlgconfig.configcontext import ConfigContext
from ..sagisgndlgconfig import sagisgndlgconfig_utils
from ..sagisgndlgconfig.sagis_gn_dlg_config import SagisGnDlgConfig


class DialogTab(QScrollArea):
    def __init__(self, context: ConfigContext,
                 panel: SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel,
                 parent=None):
        super().__init__(parent)
        self.context = context
        self.panel = panel

        self.setWidgetResizable(True)
        self.setWidget(QWidget())
        self.widget().setLayout(QVBoxLayout())
        self.widget().layout().setSpacing(0)
        self.widget().layout().setContentsMargins(0, 0, 0, 0)
        self.widget().setStyleSheet("background-color: #edf5ff")

        self.data: list[dict] = []
        self.items: list[DialogItem] = []

    def result_count(self) -> int:
        return len(self.data)

    def get_data(self):
        self.data = []

        name = self.panel.query.name
        if name and name in self.context.data_dicts:
            self.data = self.context.data_dicts.get(name, [])
            return

        sql = self.panel.query.sql
        if not sql:
            return

        sql = sagisgndlgconfig_utils.replace_schema_placeholder(sql, self.context.config)

        parent = self.panel.query.parent
        if parent and parent not in self.context.data_dicts:
            return

        if parent:
            parent_data = self.context.data_dicts.get(parent)
            if parent_data:
                success, sql = commonfunctions.insert_dict_values_into_string(sql, parent_data[0])
                if not success:
                    return

        self.data = self.context.datasource.select_into_dict_list(sql, null_value_to_none=True)
        if not self.data and self.context.datasource.error_text:
            loggerutils.log_error(f"Fehler (DialogTab):\n{self.context.datasource.error_text}")

        if name:
            self.context.data_dicts[name] = self.data

    def add_items(self):
        for i in reversed(range(self.widget().layout().count())):
            self.widget().layout().itemAt(i).widget().setParent(None)

        for item in self.items:
            item.deleteLater()

        self.items = []

        for index, data in enumerate(self.data):
            item = self.add_item(index + 1, data)
            if item == -1:
                break
            if not item:
                continue
            # Change alternative background color
            if index % 2 != 0:
                item.setStyleSheet("background-color: #bfd4ee")

            item.populate()
            self.widget().layout().addWidget(item)
            self.items.append(item)

        # Let added widgets keep their height
        self.widget().layout().addWidget(QWidget())

    def add_item(self, index: int, data: dict) -> Union[DialogItem, int, None]:
        if not self.panel.item_template:
            return
        template = self.panel.item_template.split("\\")
        try:
            import_string = f"from ..resources.config.GenericDialog.itemtemplates.{template[-2].lower()}.{template[-1].lower()} import {template[-1]} as item_template"
            exec(import_string, globals())
            # noinspection PyUnresolvedReferences
            item = item_template(self.context, self.panel, data, index, self.result_count())
            self.widget().layout().addWidget(item)
            return item
        except ModuleNotFoundError as e:
            loggerutils.log_error(f"Fehler (DialogTab):\n{str(e)}")
            return -1
        except Exception as e:
            loggerutils.log_error(f"Fehler (DialogTab):\n{str(e)}")
            return None

    def update_items(self):
        self.get_data()
        self.add_items()
