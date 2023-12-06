from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from qgis.core import QgsDataSourceUri, QgsLayerTreeGroup, QgsProject

from ..datasources.datasource import DataSource
from ..datasources.postgresdatasource import PostgresDataSource
from ..datasources.sqlitedatasource import SqliteDataSource


class AlkisDataSourceType(str, Enum):
    SAGisPgSql = "SAGisPgSql"
    SAGisSqlite = "SAGisSqlite"


@dataclass
class TableInfo:
    table_name: str
    caption: str
    geom_column: str
    primary_key_column: str
    type: Any = None
    style_name: str = ""
    display_expression: str = ""
    layer_id: str = ""


class AlkisDataSource(DataSource, ABC):
    PROJECT_ENTRY_SCOPE = "sagis_alkis_search"

    def __init__(self, uri: QgsDataSourceUri):
        super().__init__(uri)

        # Set during initialization
        self.f_class_name = ""
        self.datasource_type: Optional[AlkisDataSourceType] = None
        self.config_file = ""

        # Set in add_layers()
        self.main_group: Optional[QgsLayerTreeGroup] = None
        self.group_basemap: Optional[QgsLayerTreeGroup] = None
        self.group_owner_category: Optional[QgsLayerTreeGroup] = None
        self.group_special_entries: Optional[QgsLayerTreeGroup] = None
        self.street_result_layer = ""
        self.building_result_layer = ""
        self.flurstueck_result_layer = ""
        self.flurstueck_primary_key = ""

    def save_result_layers(self) -> None:
        p = QgsProject.instance()
        p.writeEntry(self.PROJECT_ENTRY_SCOPE, "datasourcetype", self.datasource_type)
        p.writeEntry(self.PROJECT_ENTRY_SCOPE, "street_result_layer", self.street_result_layer)
        p.writeEntry(self.PROJECT_ENTRY_SCOPE, "building_result_layer", self.building_result_layer)
        p.writeEntry(self.PROJECT_ENTRY_SCOPE, "flurstueck_result_layer", self.flurstueck_result_layer)

    @abstractmethod
    def add_layers(self) -> None:
        self.main_group = QgsProject.instance().layerTreeRoot().addGroup("ALKIS")
        self.group_basemap = self.main_group.addGroup("Grundkarte")
        self.group_owner_category = self.main_group.addGroup("Eigentümerkategorie")
        self.group_special_entries = self.main_group.addGroup("Sondereinträge")
        self.main_group.setExpanded(False)
        self.group_basemap.setExpanded(False)
        self.group_owner_category.setExpanded(False)
        self.group_special_entries.setExpanded(False)
        self.group_owner_category.setItemVisibilityChecked(False)
        self.group_special_entries.setItemVisibilityChecked(False)

    # Street search
    @abstractmethod
    def get_streetnames(self) -> list[dict]:
        pass

    # House number search
    @abstractmethod
    def get_municipalities(self) -> list[dict]:
        pass

    @abstractmethod
    def get_streets(self, municipality_id: int) -> list[dict]:
        pass

    @abstractmethod
    def get_numbers(self, street_key: str) -> list[dict]:
        pass

    # Flurstück search
    @abstractmethod
    def get_bundesland(self) -> Any:
        pass

    @abstractmethod
    def get_gemarkungen(self) -> list[dict]:
        pass

    @abstractmethod
    def search_flurstuecke(self, fsk="", gmk_gmn="", fln="", fsn_zae="", fsn_nen="") -> list[dict]:
        pass


class AlkisDataSourcePostgres(AlkisDataSource, PostgresDataSource, ABC):
    ...


class AlkisDataSourceSqlite(AlkisDataSource, SqliteDataSource, ABC):
    ...
