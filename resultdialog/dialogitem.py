from abc import ABC, abstractmethod
from typing import Any

from PyQt5.QtWidgets import QSizePolicy, QFrame

from .dialogbindingwidget import DialogBindingWidget
from .. import utils
from ..sagisgndlgconfig.configcontext import ConfigContext
from ..sagisgndlgconfig.sagis_gn_dlg_config import SagisGnDlgConfig


class DialogItem(QFrame):
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

        self.binding_widgets: dict[str, DialogBindingWidget] = {}

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

    def set_index(self, current: int, total: int):
        index_label = self.__dict__.get("labelCurrentIndex")
        if index_label:
            index_label.setText(f"{current}/{total}")

    def get_value(self, key: str, default="") -> Any:
        value = utils.get_case_insensitive(self.data, key, default)
        return value if value else default

    def bind_table_view(self, binding: SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel.Bindings):
        if not binding.active:
            return

        bind_to = binding.bind_to
        if not bind_to:
            return

        binding_widget = self.__dict__.get(bind_to)
        if not isinstance(binding_widget, DialogBindingWidget):
            return

        binding_widget.bind(self.context, binding)
        self.binding_widgets[bind_to] = binding_widget

        if binding.caption:
            binding_widget.set_caption(binding.caption)

    def populate(self):
        self.set_index(self.object_index, self.total_objects)
        self.set_label_texts()

        if not self.binding_widgets:
            for binding in self.panel.bindings:
                self.bind_table_view(binding)

        for binding_widget in self.binding_widgets.values():
            binding_widget.update_input_data(self.data)

    @abstractmethod
    def set_label_texts(self):
        ...
