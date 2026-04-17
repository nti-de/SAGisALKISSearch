from ..sagisgndlgconfig.sagis_gn_dlg_config import SagisGnDlgConfig


def replace_schema_placeholder(sql: str, config: SagisGnDlgConfig) -> str:
    placeholder = config.container.schema_name_place_holder
    if not sql or not placeholder:
        return sql
    schema = config.container.schema_name if config.container.schema_name else ""
    return sql.replace(placeholder, schema)


def insert_object_id(sql: str, object_id: any) -> str:
    placeholder = "{SELECTED_MAP_ITEM}"
    # Add single quotes to string
    object_id_str = f"'{object_id}'" if isinstance(object_id, str) else str(object_id)
    return sql.replace(placeholder, object_id_str)
