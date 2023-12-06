import os
import pathlib
import sys
from typing import Optional

from qgis.core import QgsProject

from . import loggerutils
from .datasources.datasource import DataSource
from .resultdialog.genericdialog import GenericDialog
from .sagisgndlgconfig.configcontext import ConfigContext
from .sagisgndlgconfig.sagis_gn_dlg_config import SagisGnDlgConfig


class ResultDialogBuilder:
    result_dialogs = []

    def __init__(self, result_list: list[dict], class_name: str, primary_key_name: str, datasource: DataSource, config_path: str):
        self.result_list = result_list
        self.class_name = class_name
        self.primary_key_name = primary_key_name  # Could also come from datasource.flurstueck_primary_key
        self.datasource = datasource
        self.config_path = config_path

        self.config: Optional[SagisGnDlgConfig] = None
        self.valid = False
        self.valid = self.read_config()

    def read_config(self) -> bool:
        # Import XmlParser
        from xsdata.formats.dataclass.parsers import XmlParser

        try:
            absolute_path = os.path.join(pathlib.Path(__file__).parent, pathlib.Path(self.config_path).__str__().lstrip("\\/"))
            xml_file = pathlib.Path(absolute_path).read_text()
            parser = XmlParser()
            self.config = parser.from_string(xml_file, SagisGnDlgConfig)
            return True
        except Exception as e:
            loggerutils.log_error(f"Fehler beim Lesen der Konfigurationsdateien:\n{str(e)}")
            self.config = None
            return False

    def build(self):
        if not self.valid:
            return
        layer_id, ok = QgsProject.instance().readEntry("sagis_alkis_search", "flurstueck_result_layer")
        result_layer = QgsProject.instance().mapLayer(layer_id) if ok else None

        # Copy datasource
        datasource = type(self.datasource)(self.datasource.uri)
        if not datasource.connection_success:
            loggerutils.log_error(f"Fehler (ResultDialogBuilder):\n{datasource.error_text}")
            return

        context = ConfigContext(
            class_name=self.class_name,
            config=self.config,
            datasource=datasource,
            primary_key_name=self.primary_key_name,
            result_layer=result_layer
        )
        dlg = GenericDialog(context, self.result_list.copy())
        self.result_dialogs.append(dlg)
        dlg.closed.connect(lambda: self.result_dialogs.remove(dlg))
        dlg.show()
