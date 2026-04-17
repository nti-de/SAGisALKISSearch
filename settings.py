from enum import Enum
from typing import Any, Optional
from qgis.core import QgsSettings

from .alkisdatasources.alkisdatasource import AlkisDataSourceType

SAGIS_ALKIS_SEARCH_PATH = "SAGis/SAGisALKISSearch"


def save_setting(key, value):
    settings = QgsSettings()
    setting_key = f"{SAGIS_ALKIS_SEARCH_PATH}/settings/{key}"
    if isinstance(value, Enum):
        settings.setValue(setting_key, value.value)
    elif value is not None:
        settings.setValue(setting_key, value)
    else:
        settings.remove(setting_key)


def load_setting(key, type_: type, default_value=None) -> Any:
    settings = QgsSettings()
    setting_key = f"{SAGIS_ALKIS_SEARCH_PATH}/settings/{key}"

    if issubclass(type_, Enum):
        try:
            value = settings.value(setting_key)
            if value is None:
                return default_value
            return type_(value)
        except ValueError:
            return default_value

    return settings.value(setting_key, default_value, type_)


def connection() -> str:
    return load_setting("connection", str, "")


def set_connection(value: Optional[str]) -> None:
    save_setting("connection", value)


def file() -> str:
    return load_setting("file", str, "")


def set_file(value: Optional[str]) -> None:
    save_setting("file", value)


def datasourcetype() -> Optional[AlkisDataSourceType]:
    return load_setting("datasourcetype", AlkisDataSourceType, None)


def set_datasourcetype(value: Optional[AlkisDataSourceType]) -> None:
    save_setting("datasourcetype", value)


def layers_readonly():
    return load_setting("layers_readonly", bool, True)


def set_layers_readonly(value: bool) -> None:
    save_setting("layers_readonly", value)


def layers_required():
    return load_setting("layers_required", bool, False)


def set_layers_required(value: bool) -> None:
    save_setting("layers_required", value)


def sagisweburl() -> str:
    return load_setting("sagisweburl", str, "")


def set_sagisweburl(value: str) -> None:
    save_setting("sagisweburl", value)
