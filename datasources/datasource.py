from abc import ABC, abstractmethod
from qgis.core import QgsAbstractDatabaseProviderConnection

from .featuresourceprovidertype import FeatureSourceProviderType


class DataSource(ABC):
    def __init__(self, connection: QgsAbstractDatabaseProviderConnection):
        self.connection = connection
        self.connection_success, self.error_text = True, None
        self.feature_source_provider_type: FeatureSourceProviderType = FeatureSourceProviderType.Unknown
        self.set_layers_readonly = True
        self.set_layers_required = False

    @abstractmethod
    def select_into_dict_list(self, sql: str) -> list[dict]:
        pass

    @abstractmethod
    def get_column_names(self, table_name: str, force_lower=False) -> list[str]:
        pass

    @abstractmethod
    def get_geom_columns(self, table_name: str, force_lower=False) -> list[str]:
        pass

    @abstractmethod
    def get_generic_select_statement(self, table_name: str, column_list=None) -> str:
        pass
