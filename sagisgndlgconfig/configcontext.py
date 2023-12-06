from dataclasses import dataclass, field
from qgis.core import QgsVectorLayer

from .sagis_gn_dlg_config import SagisGnDlgConfig
from ..datasources.datasource import DataSource


@dataclass
class ConfigContext:
    class_name: str  # Could also come from datasource.f_class_name
    config: SagisGnDlgConfig
    datasource: DataSource
    primary_key_name: str
    result_layer: QgsVectorLayer = None
    data_dicts: dict[str, list[dict]] = field(default_factory=dict)  # Query name: list of results as dicts

    # TODO: Check if primary_key_name is in data_dicts
