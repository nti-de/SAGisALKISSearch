from typing import Any, Optional

from . import settings
from .alkisdatasources.alkisdatasource import AlkisDataSource, AlkisDataSourceType
from .alkisdatasources.sagisconverter import SagisConverter
from .alkisdatasources.sqlitesagisconverter import SqliteSagisConverter
from .datasources import postgreshelper, sqlitehelper


def get_case_insensitive(dictionary: dict, key, default=None) -> Any:
    for k, v in dictionary.items():
        if k.lower() == key.lower():
            return v
    return default


def create_datasource() -> Optional[AlkisDataSource]:
    datasource_type = settings.datasourcetype()
    if datasource_type == AlkisDataSourceType.SAGisPgSql:
        connection = postgreshelper.get_connection(settings.connection())
        datasource = SagisConverter(connection)
    elif datasource_type == AlkisDataSourceType.SAGisSqlite:
        connection = sqlitehelper.get_connection(settings.file())
        datasource = SqliteSagisConverter(connection)
    else:
        datasource = None
    return datasource
