from typing import List
from qgis.PyQt.QtCore import QAbstractTableModel, Qt


class SqlResultModel(QAbstractTableModel):
    def __init__(self, data: List[dict], parent=None):
        super().__init__(parent)
        self._data = data
        self._field_names = list(data[0].keys()) if self._data else []
        self._headers = dict(zip(self._field_names, self._field_names)) if self._field_names else {}

    def rowCount(self, parent=None) -> int:
        return len(self._data)

    def columnCount(self, parent=None) -> int:
        return len(self._field_names)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            row = self._data[index.row()]
            key = self._field_names[index.column()]
            return row.get(key)

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            key = self._field_names[section]
            return self._headers.get(key)

        return section + 1

    def setHeaderData(self, section, orientation, value, role=None):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            key = self._field_names[section]
            self._headers[key] = value
            self.headerDataChanged.emit(orientation, section, section)
            return True

        return False
