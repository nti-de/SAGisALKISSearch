import uuid
from typing import Optional

from qgis.PyQt.QtSql import QSqlDatabase
from qgis.core import QgsAbstractDatabaseProviderConnection, QgsDataSourceUri


class QSqlConnectionContext:
    def __init__(self, connection: QgsAbstractDatabaseProviderConnection):
        self._qgis_connection = connection
        self._database_name = "sagis_" + uuid.uuid4().hex
        self._qsql_database: Optional[QSqlDatabase] = None

    def __enter__(self):
        self._qsql_database = self._convert_to_qsql_connection()

        if not self._qsql_database.open():
            raise RuntimeError(f"Failed to open database: {self._qsql_database.lastError().text()}")

        return self._qsql_database

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._qsql_database:
            self._qsql_database.close()
            QSqlDatabase.removeDatabase(self._database_name)
            self._qsql_database = None

    def _convert_to_qsql_connection(self) -> QSqlDatabase:
        uri = QgsDataSourceUri(self._qgis_connection.uri())
        provider = self._qgis_connection.providerKey()

        if provider == "postgres":
            resolved_uri = QgsDataSourceUri(uri.uri())
            db = QSqlDatabase.addDatabase("QPSQL", self._database_name)
            db.setHostName(resolved_uri.host() or "localhost")
            db.setPort(int(resolved_uri.port()) if resolved_uri.port() else 5432)
            db.setDatabaseName(resolved_uri.database())
            db.setUserName(resolved_uri.username())
            db.setPassword(resolved_uri.password())

        elif provider == "ogr":
            db = QSqlDatabase.addDatabase("QSQLITE", self._database_name)
            db.setDatabaseName(self._qgis_connection.uri())

        else:
            raise RuntimeError(f"Unsupported database provider: {provider}")

        return db
