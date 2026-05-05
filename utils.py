from typing import Any, Optional

from qgis.core import QgsMapLayer

from . import settings
from .alkisdatasources.alkisdatasource import AlkisDataSource, AlkisDataSourceType
from .alkisdatasources.sagisconverter import SagisConverter
from .alkisdatasources.sqlitesagisconverter import SqliteSagisConverter
from .datasources import postgreshelper, sqlitehelper


def get_case_insensitive(dictionary: dict[str, Any], key: str, default=None) -> Any:
    # Try as is.
    if key in dictionary:
        return dictionary[key]

    # Now it's important that the key is str.
    if not isinstance(key, str):
        raise TypeError(f"key must be str, not {type(key)}")

    key = key.casefold()
    for k, v in dictionary.items():
        if isinstance(k, str) and k.casefold() == key:
            return v
    return default


def create_datasource() -> Optional[AlkisDataSource]:
    datasource_type = settings.datasourcetype()
    if datasource_type == AlkisDataSourceType.SAGisPgSql:
        connection = postgreshelper.get_connection(settings.connection())
        datasource = SagisConverter(connection) if connection else None
    elif datasource_type == AlkisDataSourceType.SAGisSqlite:
        connection = sqlitehelper.get_connection(settings.file())
        datasource = SqliteSagisConverter(connection) if connection else None
    else:
        datasource = None

    if datasource:
        datasource.set_layers_readonly = settings.layers_readonly()
        datasource.set_layers_required = settings.layers_required()

    return datasource


def set_layer_required(layer: QgsMapLayer, required: bool) -> None:
    flags = layer.flags()

    if required:
        flags &= ~QgsMapLayer.LayerFlag.Removable
    else:
        flags |= QgsMapLayer.LayerFlag.Removable

    layer.setFlags(QgsMapLayer.LayerFlag(flags))
