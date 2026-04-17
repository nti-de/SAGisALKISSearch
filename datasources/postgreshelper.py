from typing import Optional
from qgis.core import QgsAbstractDatabaseProviderConnection, QgsProviderRegistry


def get_connection(connection_name: str) -> Optional[QgsAbstractDatabaseProviderConnection]:
    connection: QgsAbstractDatabaseProviderConnection = QgsProviderRegistry.instance().providerMetadata('postgres').connections()[connection_name]
    return connection
