from typing import Optional
from qgis.core import QgsAbstractDatabaseProviderConnection, QgsProviderRegistry


def get_connection(database_path: str) ->Optional[QgsAbstractDatabaseProviderConnection]:
    md = QgsProviderRegistry.instance().providerMetadata("ogr")
    conn = md.createConnection(database_path, {})
    return conn
