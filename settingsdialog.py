import configparser
import os

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QMessageBox
from qgis.PyQt import uic, QtGui
from qgis.core import QgsSettings

from . import loggerutils
from . import settings
from . import utils
from .alkisdatasources.alkisdatasource import AlkisDataSourceType

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "ui/settings.ui"))
POSTGRESQL_CONNECTION_PATH = "PostgreSQL/connections"
DEFAULT_USER = "postgres"
DEFAULT_SCHEMA = "public"


class SettingsDialog(QDialog, FORM_CLASS):
    # TODO: Save settings per project

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.set_version_label()
        self.connection_names = []

        self.rbSagisPostgres.toggled.connect(self.datasource_type_changed)
        self.rbSagisSqlite.toggled.connect(self.datasource_type_changed)

        self.leUser.setPlaceholderText(DEFAULT_USER)

        self.bAddLayers = self.buttonBox.addButton("Speichern und Layer hinzufügen", QDialogButtonBox.ActionRole)
        self.bAddLayers.clicked.connect(self.add_layers_clicked)

        self.cbConnections.currentTextChanged.connect(self.connection_changed)
        self.accepted.connect(self.save_settings)

        self.read_ini()

    def showEvent(self, e: QtGui.QShowEvent) -> None:
        super().showEvent(e)
        self.populate_connections()
        self.load_settings()

    def populate_connections(self):
        self.cbConnections.clear()

        s = QgsSettings()
        s.beginGroup(POSTGRESQL_CONNECTION_PATH)
        self.connection_names = [name for name in s.childGroups()]
        s.endGroup()

        self.cbConnections.addItems(self.connection_names)

    def datasource_type_changed(self):
        if self.rbSagisPostgres.isChecked():
            self.groupBoxConnection.setEnabled(True)
            self.groupBoxFile.setEnabled(False)
        elif self.rbSagisSqlite.isChecked():
            self.groupBoxConnection.setEnabled(False)
            self.groupBoxFile.setEnabled(True)
        else:
            self.groupBoxConnection.setEnabled(False)
            self.groupBoxFile.setEnabled(False)

    def connection_changed(self, connection_name: str):
        s = QgsSettings()
        user = s.value(f"{POSTGRESQL_CONNECTION_PATH}/{connection_name}/username", "")
        password = s.value(f"{POSTGRESQL_CONNECTION_PATH}/{connection_name}/password", "")
        self.leUser.setText(user)
        self.lePassword.setText(password)

    def save_settings(self):
        # Datasource type
        if self.rbSagisPostgres.isChecked():
            datasource_type = AlkisDataSourceType.SAGisPgSql
        elif self.rbSagisSqlite.isChecked():
            datasource_type = AlkisDataSourceType.SAGisSqlite
        else:
            datasource_type = None
        settings.set_datasourcetype(datasource_type)

        # Connection
        settings.set_connection(self.cbConnections.currentText())
        user = self.leUser.text() if self.leUser.text() else DEFAULT_USER
        settings.set_user(user)
        settings.set_password(self.lePassword.text())

        # SQLite file path
        settings.set_file(self.mQgsFileWidget.filePath())

        # SAGis web URL
        settings.set_sagisweburl(self.leSagiswebUrl.text())

    def load_settings(self):
        # Connection
        saved_connection = settings.connection()
        if saved_connection in self.connection_names:
            index = self.cbConnections.findText(saved_connection)
            self.cbConnections.setCurrentIndex(index)
            self.leUser.setText(settings.user())
            self.lePassword.setText(settings.password())

        # SQLite file path
        self.mQgsFileWidget.setFilePath(settings.file())

        # Datasource type
        datasource_type = settings.datasourcetype()
        if datasource_type == AlkisDataSourceType.SAGisPgSql and self.rbSagisPostgres.isVisible():
            self.rbSagisPostgres.setChecked(True)
        elif datasource_type == AlkisDataSourceType.SAGisSqlite and self.rbSagisSqlite.isVisible():
            self.rbSagisSqlite.setChecked(True)
        else:
            self.rbSagisPostgres.setChecked(False)
            self.rbSagisSqlite.setChecked(False)

        # SAGis web URL
        self.leSagiswebUrl.setText(settings.sagisweburl())

    def add_layers_clicked(self):
        self.save_settings()

        # Check if database connection is selected when a Postgres datasource is selected.
        if self.groupBoxConnection.isEnabled() and self.cbConnections.currentIndex() == -1:
            QMessageBox.information(self, self.windowTitle(), "Keine Verbindung gewählt.")
            return

        # Check if file exists when a SQLite datasource is selected.
        if self.groupBoxFile.isEnabled() and not os.path.isfile(settings.file()):
            QMessageBox.information(self, self.windowTitle(), "Angegebene SQLite-Datei existiert nicht.")
            return

        datasource = utils.create_datasource()
        if not datasource:
            QMessageBox.information(self, self.windowTitle(), "Keine Datenquelle gewählt.")
            return

        if datasource.error_text:
            loggerutils.log_warning(datasource.error_text, title=self.windowTitle())
            return

        datasource.add_layers()
        self.close()

    def read_ini(self):
        config = configparser.ConfigParser()
        path = os.path.join(os.path.dirname(__file__), "SAGisALKISSearch.ini")
        config.read(path)
        section = "DataSources"

        self.rbSagisPostgres.setVisible(config.getboolean(section, "SAGisPgSql", fallback=True))
        self.rbSagisSqlite.setVisible(config.getboolean(section, "SAGisSqlite", fallback=True))

    def set_version_label(self):
        metadata_parser = configparser.ConfigParser()
        path = os.path.join(os.path.dirname(__file__), "metadata.txt")
        metadata_parser.read(path)
        self.labelVersion.setText(metadata_parser.get("general", "version", fallback=""))
