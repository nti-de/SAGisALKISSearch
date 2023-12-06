from typing import Optional

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtSql import QSqlQueryModel
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QTableView, QHeaderView, QFrame, QSizePolicy

from .. import commonfunctions
from .. import loggerutils
from ..sagisgndlgconfig import sagisgndlgconfig_utils
from ..sagisgndlgconfig.configcontext import ConfigContext
from ..sagisgndlgconfig.sagis_gn_dlg_config import SagisGnDlgConfig


class DialogBindingWidget(QFrame):
    def __init__(self, set_visible=False, parent=None):
        super().__init__(parent)
        # Hidden by default, changed if model has rows
        self.setVisible(set_visible)

        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)
        self.caption_label = QLabel()
        self.caption_label.setAlignment(Qt.AlignHCenter)

        self.table_view = QTableView()
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setStyleSheet("alternate-background-color: #bfd4ee; background-color: #edf5ff")
        self.layout().addWidget(self.table_view)

        self.context: Optional[ConfigContext] = None
        self.binding: Optional[SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel.Bindings] = None
        self.input_data = {}

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def sizeHint(self) -> QSize:
        left = self.layout().contentsMargins().left()
        right = self.layout().contentsMargins().right()
        width = self.table_view.width() + left + right

        height = self.table_view.height() + self.caption_label.sizeHint().height()
        return QSize(width, height)

    def set_caption(self, caption: Optional[str]):
        # if isinstance(caption, str):
        if caption:
            self.caption_label.setText(caption)
            if self.layout().indexOf(self.caption_label) == -1:
                self.layout().insertWidget(0, self.caption_label, Qt.AlignHCenter)
        else:
            self.caption_label.setText("")
            self.layout().removeWidget(self.caption_label)

    def bind(self, context: ConfigContext, binding: SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel.Bindings):
        self.context = context
        self.binding = binding

    def populate(self):
        self.table_view.setModel(QSqlQueryModel())
        if not self.input_data:
            return

        if not self.context or not self.binding:
            return

        db = self.context.datasource.database
        if not db or not self.binding.sql:
            return

        if not db.isOpen():
            db.open()

        sql = sagisgndlgconfig_utils.replace_schema_placeholder(self.binding.sql, self.context.config)
        success, sql = commonfunctions.insert_dict_values_into_string(sql, self.input_data)
        if not success:
            loggerutils.log_error(f"Fehler (DialogBindingWidget):\nAbfrageergebnis enthält nicht '{sql}'")
            return

        self.table_view.model().setQuery(sql, db)
        # Hide if there are no results
        self.setVisible(self.table_view.model().rowCount() > 0)
        self.rename_columns()
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.resize_table_to_content()

    def update_input_data(self, input_data: dict):
        self.input_data = input_data
        self.populate()

    def resize_table_to_content(self):
        total_height = self.table_view.horizontalHeader().height() + 2
        for row in range(self.table_view.model().rowCount()):
            total_height += self.table_view.rowHeight(row)
        self.table_view.setFixedHeight(total_height)

        total_width = 2
        for column in range(self.table_view.model().columnCount()):
            total_width += self.table_view.columnWidth(column)
        self.table_view.setFixedWidth(total_width)

    def rename_columns(self, sort_by_header_text=False):
        """If header texts are provided, only the included columns are shown, the rest will be hidden."""

        if not self.binding.header_text or not self.table_view.model():
            return

        def get_logical_index(text: str):
            for i in range(self.table_view.model().columnCount()):
                if self.table_view.model().headerData(i, Qt.Horizontal, Qt.DisplayRole) == text:
                    return i
            return -1

        shown_columns = []
        for index, header_text in reversed(list(enumerate(self.binding.header_text))):

            logical_index = get_logical_index(header_text.from_value.lower())
            if logical_index == -1:
                continue

            # Change position
            if sort_by_header_text:
                header = self.table_view.horizontalHeader()
                visual_index = header.visualIndex(logical_index)
                header.moveSection(visual_index, 0)

            # Rename header
            self.table_view.model().setHeaderData(logical_index, Qt.Horizontal, header_text.to, Qt.DisplayRole)

            shown_columns.append(logical_index)

        # Hide remaining columns
        for column in range(self.table_view.model().columnCount()):
            if column not in shown_columns:
                self.table_view.setColumnHidden(column, True)
