from typing import Tuple

from qgis.core import QgsAbstractDatabaseProviderConnection


def select_into_dict_list(sql: str, connection: QgsAbstractDatabaseProviderConnection) -> Tuple[list[dict], str]:
    result = []
    error_text = ""

    try:
        query_result = connection.execSql(sql)
        columns = query_result.columns()
        while query_result.hasNextRow():
            row = query_result.nextRow()
            d = dict(zip(columns, row))
            result.append(d)
    except Exception as e:
        error_text = str(e)

    return result, error_text


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
