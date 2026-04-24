from qgis.core import QgsAbstractDatabaseProviderConnection

from . import databasehelper
from .datasource import DataSource
from .featuresourceprovidertype import FeatureSourceProviderType


class SqliteDataSource(DataSource):
    def __init__(self, connection: QgsAbstractDatabaseProviderConnection):
        super().__init__(connection)
        self.feature_source_provider_type = FeatureSourceProviderType.Sqlite

    def select_into_dict_list(self, sql: str) -> list[dict]:
        result, self.error_text = databasehelper.select_into_dict_list(sql, self.connection)
        # Unlike PostgreSQL, SQLite has uppercase column names. --> Uncomment if necessary
        # result_lower = [{k.lower(): v for k, v in row.items()} for row in result]
        # return result_lower
        return result

    def get_column_names(self, table_name: str, force_lower=False) -> list[str]:
        result, self.error_text = databasehelper.get_column_names(self.connection, "public", table_name)
        return [c.lower() for c in result] if force_lower else result

    def get_geom_columns(self, table_name: str, force_lower=False) -> list[str]:
        result, self.error_text = databasehelper.get_geom_columns(self.connection, "public", table_name)
        return result

    def get_generic_select_statement(self, table_name: str, column_list=None) -> str:
        if not column_list:
            column_list = self.get_column_names(table_name)

        sql = "SELECT {columns} FROM {table_name}"
        sql = sql.format(columns=", ".join(column_list), table_name=table_name)
        return sql