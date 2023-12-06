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


def user() -> str:
    return load_setting("user", str, "")


def set_user(value: Optional[str]) -> None:
    save_setting("user", value)


def password() -> str:
    return load_setting("password", str, "")


def set_password(value: Optional[str]) -> None:
    save_setting("password", value)


def schema() -> str:
    return load_setting("schema", str, "")


def set_schema(value: Optional[str]) -> None:
    save_setting("schema", value)


def file() -> str:
    return load_setting("file", str, "")


def set_file(value: Optional[str]) -> None:
    save_setting("file", value)


def datasourcetype() -> Optional[AlkisDataSourceType]:
    return load_setting("datasourcetype", AlkisDataSourceType, None)


def set_datasourcetype(value: Optional[AlkisDataSourceType]) -> None:
    save_setting("datasourcetype", value)


def sagisweburl() -> str:
    return load_setting("sagisweburl", str, "")


def set_sagisweburl(value: str) -> None:
    save_setting("sagisweburl", value)
