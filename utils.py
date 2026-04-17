from typing import Any, Optional

from qgis.core import QgsMapLayer

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
