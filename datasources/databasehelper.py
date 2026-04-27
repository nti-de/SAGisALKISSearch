from typing import Tuple

from qgis.PyQt import QtCore
from qgis.PyQt.QtSql import QSqlQuery
from qgis.core import QgsAbstractDatabaseProviderConnection

from .qsqlconnectioncontext import QSqlConnectionContext


if QtCore.PYQT_VERSION_STR.startswith("5"):
    from qgis.PyQt.QtCore import QVariant
    def _is_null(value) -> bool:
        return isinstance(value, QVariant) and value.isNull()
else:
    def _is_null(value) -> bool:
        return value is None


def select_into_dict_list(sql: str, connection: QgsAbstractDatabaseProviderConnection) -> Tuple[list[dict], str]:
    provider = connection.providerKey()
    if provider == "postgres":
        result, error_text = select_into_dict_list_qgis(sql, connection)
    elif provider == "ogr":
        result, error_text = select_into_dict_list_qsql(sql, connection)
    else:
        raise RuntimeError(f"Unsupported database provider: {provider}")

    return result, error_text


def select_into_dict_list_qgis(sql: str, connection: QgsAbstractDatabaseProviderConnection) -> Tuple[list[dict], str]:
    result = []
    error_text = ""

    try:
        query_result = connection.execSql(sql)
        columns = query_result.columns()
        column_count = len(columns)

        while query_result.hasNextRow():
            row = query_result.nextRow()
            d = {}

            for i in range(column_count):
                value = row[i]
                # Convert QVariant NULL to None if needed.
                d[columns[i]] = None if _is_null(value) else value

            result.append(d)
    except Exception as e:
        error_text = str(e)

    return result, error_text


def select_into_dict_list_qsql(sql: str, connection: QgsAbstractDatabaseProviderConnection) -> Tuple[list[dict], str]:
    try:
        with QSqlConnectionContext(connection) as db:
            query = QSqlQuery(db)
            if not query.exec(sql):
                return [], query.lastError().text()

            record = query.record()
            column_count = record.count()
            column_names = [record.fieldName(i) for i in range(column_count)]

            result = []
            while query.next():
                row = {}
                for i in range(column_count):
                    value = query.value(i)
                    row[column_names[i]] = None if _is_null(value) else value
                result.append(row)

            return result, ""
    except RuntimeError as e:
        return [], str(e)


def get_column_names(connection: QgsAbstractDatabaseProviderConnection, table_schema: str, table_name: str) -> Tuple[list[str], str]:
    try:
        fields = connection.fields(table_schema, table_name)
        return fields.names(), ""
    except Exception as e:
        return [], str(e)


def get_geom_columns(connection: QgsAbstractDatabaseProviderConnection, table_schema: str, table_name: str) -> Tuple[list[str], str]:
    try:
        table =  connection.table(table_schema, table_name)
        return [table.geometryColumn()], ""
    except Exception as e:
        return [], str(e)
