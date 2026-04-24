from qgis.core import QgsAbstractDatabaseProviderConnection

from . import databasehelper
from .datasource import DataSource
from .featuresourceprovidertype import FeatureSourceProviderType


class PostgresDataSource(DataSource):
    def __init__(self, connection: QgsAbstractDatabaseProviderConnection):
        super().__init__(connection)
        self.feature_source_provider_type = FeatureSourceProviderType.PostgreSQL

    def select_into_dict_list(self, sql: str) -> list[dict]:
        result, self.error_text = databasehelper.select_into_dict_list(sql, self.connection)
        return result

    def get_column_names(self, table_name: str, force_lower=False) -> list[str]:
        # PostgreSQL column names are always returned as lower.
        result, self.error_text = databasehelper.get_column_names(self.connection, "public", table_name.lower())
        return result

    def get_geom_columns(self, table_name: str, force_lower=False) -> list[str]:
        # PostgreSQL column names are always returned as lower.
        result, self.error_text = databasehelper.get_geom_columns(self.connection, "public", table_name.lower())
        return result

    def get_generic_select_statement(self, table_name: str, column_list=None) -> str:
        if not column_list:
            column_list = self.get_column_names(table_name)

        geom_columns = self.get_geom_columns(table_name)
        column_list = [f"ST_AsText({c}) AS {c}" if c in geom_columns else c for c in column_list]

        sql = "SELECT {columns} FROM {table_name}"
        sql = sql.format(columns=", ".join(column_list), table_name=table_name)
        return sql
