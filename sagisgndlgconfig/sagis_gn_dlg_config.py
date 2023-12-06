from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Type


class ParameterWhereCondition(Enum):
    IN = "In"
    LIKE = "Like"
    IS_EQUAL = "IsEqual"


@dataclass
class SagisGnDlgConfig:
    class Meta:
        name = "SAGisGnDlgConfig"

    container: Optional["SagisGnDlgConfig.Container"] = field(
        default=None,
        metadata={
            "name": "Container",
            "type": "Element",
            "required": True,
        }
    )

    @dataclass
    class Container:
        caption: Optional[str] = field(
            default=None,
            metadata={
                "name": "Caption",
                "type": "Element",
                "required": True,
            }
        )
        css_files: Optional[str] = field(
            default=None,
            metadata={
                "name": "CssFiles",
                "type": "Element",
            }
        )
        schema_name_place_holder: Optional[str] = field(
            default="{SCHEMA_NAME_PLACEHOLDER}",
            metadata={
                "name": "SchemaNamePlaceHolder",
                "type": "Element",
            }
        )
        schema_name: Optional[str] = field(
            default=None,
            metadata={
                "name": "SchemaName",
                "type": "Element",
            }
        )
        activity_log: Optional["SagisGnDlgConfig.Container.ActivityLog"] = field(
            default=None,
            metadata={
                "name": "ActivityLog",
                "type": "Element",
            }
        )
        search_template: Optional["SagisGnDlgConfig.Container.SearchTemplate"] = field(
            default=None,
            metadata={
                "name": "SearchTemplate",
                "type": "Element",
                "required": True,
            }
        )
        info_template: Optional["SagisGnDlgConfig.Container.InfoTemplate"] = field(
            default=None,
            metadata={
                "name": "InfoTemplate",
                "type": "Element",
                "required": True,
            }
        )

        @dataclass
        class ActivityLog:
            active: bool = field(
                default=False,
                metadata={
                    "name": "Active",
                    "type": "Attribute",
                }
            )
            info_log_column: Optional[str] = field(
                default=None,
                metadata={
                    "name": "InfoLogColumn",
                    "type": "Attribute",
                }
            )

        @dataclass
        class SearchTemplate:
            content: List[object] = field(
                default_factory=list,
                metadata={
                    "type": "Wildcard",
                    "namespace": "##any",
                    "mixed": True,
                    "choices": (
                        {
                            "name": "Queries",
                            "type": Type["SagisGnDlgConfig.Container.SearchTemplate.Queries"],
                        },
                        {
                            "name": "Search",
                            "type": Type["SagisGnDlgConfig.Container.SearchTemplate.Search"],
                        },
                        {
                            "name": "SearchTemplate",
                            "type": str,
                        },
                    ),
                }
            )

            @dataclass
            class Queries:
                query: List["SagisGnDlgConfig.Container.SearchTemplate.Queries.Query"] = field(
                    default_factory=list,
                    metadata={
                        "name": "Query",
                        "type": "Element",
                    }
                )

                @dataclass
                class Query:
                    bind_to: Optional[str] = field(
                        default=None,
                        metadata={
                            "name": "BindTo",
                            "type": "Element",
                            "required": True,
                        }
                    )
                    sql: Optional[str] = field(
                        default=None,
                        metadata={
                            "name": "Sql",
                            "type": "Element",
                            "required": True,
                        }
                    )
                    key_value_field: Optional[str] = field(
                        default="KEY",
                        metadata={
                            "name": "KeyValueField",
                            "type": "Element",
                        }
                    )
                    caption_value_field: Optional[str] = field(
                        default="CAPTION",
                        metadata={
                            "name": "CaptionValueField",
                            "type": "Element",
                        }
                    )
                    caption_format: Optional[str] = field(
                        default="{1} ({0})",
                        metadata={
                            "name": "CaptionFormat",
                            "type": "Element",
                        }
                    )

            @dataclass
            class Search:
                sql: Optional[str] = field(
                    default=None,
                    metadata={
                        "name": "Sql",
                        "type": "Element",
                        "required": True,
                    }
                )
                fixed_sql_where: Optional[str] = field(
                    default=None,
                    metadata={
                        "name": "FixedSqlWhere",
                        "type": "Element",
                    }
                )
                parameter: List["SagisGnDlgConfig.Container.SearchTemplate.Search.Parameter"] = field(
                    default_factory=list,
                    metadata={
                        "name": "Parameter",
                        "type": "Element",
                    }
                )

                @dataclass
                class Parameter:
                    value: str = field(
                        default="",
                        metadata={
                            "required": True,
                        }
                    )
                    db_field: Optional[str] = field(
                        default=None,
                        metadata={
                            "name": "DbField",
                            "type": "Attribute",
                            "required": True,
                        }
                    )
                    form_field: Optional[str] = field(
                        default=None,
                        metadata={
                            "name": "FormField",
                            "type": "Attribute",
                            "required": True,
                        }
                    )
                    db_joined_table_name: str = field(
                        default="",
                        metadata={
                            "name": "DbJoinedTableName",
                            "type": "Attribute",
                        }
                    )
                    db_table_alias: str = field(
                        default="",
                        metadata={
                            "name": "DbTableAlias",
                            "type": "Attribute",
                        }
                    )
                    default_value: str = field(
                        default="",
                        metadata={
                            "name": "DefaultValue",
                            "type": "Attribute",
                        }
                    )
                    case_sensitive: bool = field(
                        default=True,
                        metadata={
                            "name": "CaseSensitive",
                            "type": "Attribute",
                        }
                    )
                    range: bool = field(
                        default=False,
                        metadata={
                            "name": "Range",
                            "type": "Attribute",
                        }
                    )
                    where_condition: ParameterWhereCondition = field(
                        default=ParameterWhereCondition.IS_EQUAL,
                        metadata={
                            "name": "WhereCondition",
                            "type": "Attribute",
                        }
                    )
                    sql_operator: str = field(
                        default="AND",
                        metadata={
                            "name": "SqlOperator",
                            "type": "Attribute",
                        }
                    )
                    db_field_mg_property_type: str = field(
                        default="String",
                        metadata={
                            "name": "DbFieldMgPropertyType",
                            "type": "Attribute",
                        }
                    )

        @dataclass
        class InfoTemplate:
            editable: Optional[bool] = field(
                default=True,
                metadata={
                    "name": "Editable",
                    "type": "Element",
                }
            )
            panels: Optional["SagisGnDlgConfig.Container.InfoTemplate.Panels"] = field(
                default=None,
                metadata={
                    "name": "Panels",
                    "type": "Element",
                    "required": True,
                }
            )

            @dataclass
            class Panels:
                panel: List["SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel"] = field(
                    default_factory=list,
                    metadata={
                        "name": "Panel",
                        "type": "Element",
                    }
                )

                @dataclass
                class Panel:
                    caption: Optional[str] = field(
                        default=None,
                        metadata={
                            "name": "Caption",
                            "type": "Element",
                            "required": True,
                        }
                    )
                    authorisation: Optional[str] = field(
                        default=None,
                        metadata={
                            "name": "Authorisation",
                            "type": "Element",
                        }
                    )
                    active: Optional[bool] = field(
                        default=True,
                        metadata={
                            "name": "Active",
                            "type": "Element",
                        }
                    )
                    hide_if_query_is_empty: Optional[bool] = field(
                        default=False,
                        metadata={
                            "name": "HideIfQueryIsEmpty",
                            "type": "Element",
                        }
                    )
                    show_datacount: Optional[bool] = field(
                        default=True,
                        metadata={
                            "name": "ShowDatacount",
                            "type": "Element",
                        }
                    )
                    height: Optional[int] = field(
                        default=600,
                        metadata={
                            "type": "Element",
                        }
                    )
                    query: Optional["SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel.Query"] = field(
                        default=None,
                        metadata={
                            "name": "Query",
                            "type": "Element",
                            "required": True,
                        }
                    )
                    bindings: List["SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel.Bindings"] = field(
                        default_factory=list,
                        metadata={
                            "name": "Bindings",
                            "type": "Element",
                        }
                    )
                    item_template: Optional[str] = field(
                        default=None,
                        metadata={
                            "name": "ItemTemplate",
                            "type": "Element",
                        }
                    )
                    no_item_template: Optional["SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel.NoItemTemplate"] = field(
                        default=None,
                        metadata={
                            "name": "NoItemTemplate",
                            "type": "Element",
                        }
                    )
                    footer_template: Optional[str] = field(
                        default=None,
                        metadata={
                            "name": "FooterTemplate",
                            "type": "Element",
                        }
                    )

                    @dataclass
                    class Query:
                        name: Optional[str] = field(
                            default=None,
                            metadata={
                                "name": "Name",
                                "type": "Element",
                            }
                        )
                        allow_empty: Optional[bool] = field(
                            default=True,
                            metadata={
                                "name": "AllowEmpty",
                                "type": "Element",
                            }
                        )
                        allow_max_results: Optional[int] = field(
                            default=None,
                            metadata={
                                "name": "AllowMaxResults",
                                "type": "Element",
                            }
                        )
                        parent: Optional[str] = field(
                            default=None,
                            metadata={
                                "name": "Parent",
                                "type": "Element",
                            }
                        )
                        sql: Optional[str] = field(
                            default=None,
                            metadata={
                                "name": "Sql",
                                "type": "Element",
                            }
                        )
                        intersection: Optional["SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel.Query.Intersection"] = field(
                            default=None,
                            metadata={
                                "name": "Intersection",
                                "type": "Element",
                            }
                        )
                        show_in_map: Optional["SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel.Query.ShowInMap"] = field(
                            default=None,
                            metadata={
                                "name": "ShowInMap",
                                "type": "Element",
                            }
                        )
                        js_data_columns: Optional[str] = field(
                            default=None,
                            metadata={
                                "name": "JsDataColumns",
                                "type": "Attribute",
                            }
                        )

                        @dataclass
                        class ShowInMap:
                            layer_feature_class_name: Optional[str] = field(
                                default=None,
                                metadata={
                                    "name": "LayerFeatureClassName",
                                    "type": "Element",
                                    "required": True,
                                }
                            )
                            bind_to: Optional[str] = field(
                                default=None,
                                metadata={
                                    "name": "BindTo",
                                    "type": "Element",
                                    "required": True,
                                }
                            )

                        @dataclass
                        class Intersection:
                            target_feature_class: Optional[str] = field(
                                default=None,
                                metadata={
                                    "name": "TargetFeatureClass",
                                    "type": "Element",
                                }
                            )
                            order_by: Optional[str] = field(
                                default=None,
                                metadata={
                                    "name": "OrderBy",
                                    "type": "Element",
                                }
                            )
                            filter: Optional[str] = field(
                                default=None,
                                metadata={
                                    "name": "Filter",
                                    "type": "Element",
                                }
                            )
                            mg_feature_spatial_operation: Optional[int] = field(
                                default=-1,
                                metadata={
                                    "name": "MgFeatureSpatialOperation",
                                    "type": "Element",
                                }
                            )
                            property: List[str] = field(
                                default_factory=list,
                                metadata={
                                    "name": "Property",
                                    "type": "Element",
                                }
                            )
                            translation: List["SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel.Query.Intersection.Translation"] = field(
                                default_factory=list,
                                metadata={
                                    "name": "Translation",
                                    "type": "Element",
                                }
                            )

                            @dataclass
                            class Translation:
                                sql: Optional[str] = field(
                                    default=None,
                                    metadata={
                                        "name": "Sql",
                                        "type": "Element",
                                        "required": True,
                                    }
                                )
                                from_column: Optional[str] = field(
                                    default=None,
                                    metadata={
                                        "name": "FromColumn",
                                        "type": "Element",
                                        "required": True,
                                    }
                                )
                                value_column: Optional[str] = field(
                                    default=None,
                                    metadata={
                                        "name": "ValueColumn",
                                        "type": "Element",
                                        "required": True,
                                    }
                                )
                                id_column: Optional[str] = field(
                                    default=None,
                                    metadata={
                                        "name": "IdColumn",
                                        "type": "Element",
                                        "required": True,
                                    }
                                )

                    @dataclass
                    class Bindings:
                        active: Optional[bool] = field(
                            default=True,
                            metadata={
                                "name": "Active",
                                "type": "Element",
                            }
                        )
                        caption: Optional[str] = field(
                            default=None,
                            metadata={
                                "name": "Caption",
                                "type": "Element",
                            }
                        )
                        sql: Optional[str] = field(
                            default=None,
                            metadata={
                                "name": "Sql",
                                "type": "Element",
                                "required": True,
                            }
                        )
                        bind_to: Optional[str] = field(
                            default=None,
                            metadata={
                                "name": "BindTo",
                                "type": "Element",
                                "required": True,
                            }
                        )
                        authorisation: Optional[str] = field(
                            default=None,
                            metadata={
                                "name": "Authorisation",
                                "type": "Element",
                            }
                        )
                        header_text: List["SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel.Bindings.HeaderText"] = field(
                            default_factory=list,
                            metadata={
                                "name": "HeaderText",
                                "type": "Element",
                            }
                        )
                        show_header_when_empty: Optional[bool] = field(
                            default=False,
                            metadata={
                                "name": "ShowHeaderWhenEmpty",
                                "type": "Element",
                            }
                        )
                        java_script_click: List["SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel.Bindings.JavaScriptClick"] = field(
                            default_factory=list,
                            metadata={
                                "name": "JavaScriptClick",
                                "type": "Element",
                            }
                        )

                        @dataclass
                        class HeaderText:
                            value: str = field(
                                default="",
                                metadata={
                                    "required": True,
                                }
                            )
                            from_value: Optional[str] = field(
                                default=None,
                                metadata={
                                    "name": "From",
                                    "type": "Attribute",
                                    "required": True,
                                }
                            )
                            to: Optional[str] = field(
                                default=None,
                                metadata={
                                    "name": "To",
                                    "type": "Attribute",
                                    "required": True,
                                }
                            )

                        @dataclass
                        class JavaScriptClick:
                            column: Optional[str] = field(
                                default=None,
                                metadata={
                                    "name": "Column",
                                    "type": "Element",
                                    "required": True,
                                }
                            )
                            js_fn: Optional[str] = field(
                                default=None,
                                metadata={
                                    "name": "JsFn",
                                    "type": "Element",
                                    "required": True,
                                }
                            )

                    @dataclass
                    class NoItemTemplate:
                        column_name_translation: List["SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel.NoItemTemplate.ColumnNameTranslation"] = field(
                            default_factory=list,
                            metadata={
                                "name": "ColumnNameTranslation",
                                "type": "Element",
                            }
                        )

                        @dataclass
                        class ColumnNameTranslation:
                            value: str = field(
                                default="",
                                metadata={
                                    "required": True,
                                }
                            )
                            from_value: Optional[str] = field(
                                default=None,
                                metadata={
                                    "name": "From",
                                    "type": "Attribute",
                                    "required": True,
                                }
                            )
                            to: Optional[str] = field(
                                default=None,
                                metadata={
                                    "name": "To",
                                    "type": "Attribute",
                                    "required": True,
                                }
                            )
