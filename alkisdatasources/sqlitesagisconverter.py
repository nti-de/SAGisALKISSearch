from typing import Any, Optional

from qgis.PyQt.QtXml import QDomDocument
from qgis._core import QgsCoordinateReferenceSystem
from qgis.core import QgsAbstractDatabaseProviderConnection, QgsProject, QgsVectorLayer

from .alkisdatasource import AlkisDataSourceSqlite, AlkisDataSourceType, TableInfo
from .. import utils


class SqliteSagisConverter(AlkisDataSourceSqlite):
    def __init__(self, connection: QgsAbstractDatabaseProviderConnection):
        super().__init__(connection)

        # AlkisDataSource
        self.f_class_name = "AX_FLURSTUECK"
        self.datasource_type = AlkisDataSourceType.SAGisSqlite
        self.config_file = "resources/config/GenericDialog/Configuration/AX_FLURSTUECK_SQLITE.xml"
        self.flurstueck_primary_key = "fid"

        # Geometry columns are set in the database itself (table: 'geometry_columns').
        # The same column name has to be set in layer_styles.
        # Style names currently not used. We trust in the automation for now.
        self.tables = {
            "ax_flurstueck": TableInfo("ax_flurstueck", "Flurstücke", "geom", "fid"),
            "ax_gebaeude": TableInfo("ax_gebaeude", "Gebäude", "geom", "fid"),
            "ax_flurstueck_tbl": TableInfo("ax_flurstueck_tbl", "Beschriftung Flurstück", "geom", "fid"),
            "ax_flurstueck_oa_line": TableInfo("ax_flurstueck_oa", "ALKIS_BB - AX_Flurstueck_oa", "geom", "fid",
                                               type="LineString", style_name="Flurstückslinie"),
            "ax_flurstueck_oa_arrowhead": TableInfo("ax_flurstueck_oa", "ALKIS_BB - AX_Flurstueck_oa", "geom", "fid",
                                                    type="Point", style_name="Flurstückspfeil"),
            "ax_gebaeude_tbl": TableInfo("ax_gebaeude_tbl", "Beschriftung Hausnummer", "geom", "fid"),
            "ax_lagebezohnehnr_tbl": TableInfo("ax_lagebezohnehnr_tbl", "Straßennamen", "geom", "fid")
        }

        self.standard_srs_id: Optional[int] = None
        self.standard_crs: Optional[QgsCoordinateReferenceSystem] = None

    def add_layers(self) -> None:
        super().add_layers()

        self.get_standard_crs()

        for table in self.tables.values():
            self.add_layer(table)

        self.street_result_layer = self.tables["ax_lagebezohnehnr_tbl"].layer_id
        self.building_result_layer = self.tables["ax_gebaeude"].layer_id
        self.flurstueck_result_layer = self.tables["ax_flurstueck"].layer_id
        self.save_result_layers()

    def add_layer(self, table: TableInfo):
        # Copy DataSource
        # u = QgsDataSourceUri(self.uri)
        # u.setDataSource("", table.table_name, table.geom_column, aKeyColumn=table.primary_key_column)

        # uri = f'dbname=\'{self.uri.database()}\' key=\'{table.primary_key_column}\' table="{table.table_name}" ({table.geom_column})'

        uri = f"{self.connection.uri()}|layername={table.table_name}"

        if table.type:
            uri += f"|geometrytype={table.type}"

        layer = QgsVectorLayer(uri, table.table_name, "ogr")
        layer.setName(table.caption)

        subset_string = "LZE IS NULL"
        if table.table_name in ["ax_flurstueck", "ax_gebaeude"] and self.standard_srs_id:
            subset_string += f" AND srs = {self.standard_srs_id}"

        if not layer.crs().isValid() and self.standard_crs and self.standard_crs.isValid():
            # Try to use standard CRS set in table ME_KOORDINATEnANGABEN.
            layer.setCrs(self.standard_crs)

        if table.display_expression:
            layer.setDisplayExpression(table.display_expression)

        if self.set_layers_readonly:
            layer.setReadOnly(True)

        if self.set_layers_required:
            utils.set_layer_required(layer, True)

        QgsProject.instance().addMapLayer(layer, addToLegend=False)
        tree_layer = self.group_basemap.insertLayer(0, layer)
        tree_layer.setExpanded(False)

        # Style workaround. Do not add arrow heads, set the item visibility to False.
        if table.table_name == "ax_flurstueck_oa" and table.type == "Point":
            subset_string += f" AND lower(art) != lower('Pfeilspitze')"
            tree_layer.setItemVisibilityChecked(False)

        layer.setSubsetString(subset_string)

        # Load style. Does not always happen automatically.
        # self.load_style(table, layer)

        table.layer_id = layer.id()

    def load_style(self, table: TableInfo, layer: QgsVectorLayer) -> None:
        style_tuples = layer.listStylesInDatabase()

        count = style_tuples[0]
        # Return if either the table 'layer_styles' does not exist or there is no style for the layer.
        if count <= 0:
            return

        style_ids = style_tuples[1]
        style_id = ""

        # Only one style or style name not set.
        if count == 1 or not table.style_name:
            style_id = style_ids[0]
        # Find style id by style name.
        else:
            names = style_tuples[2]
            for i, name in enumerate(names[:count]):
                if name != table.style_name:
                    continue
                style_id = style_ids[i]

        if style_id:
            style_doc = QDomDocument()
            style_tuple = layer.getStyleFromDatabase(style_id)
            style_qml = style_tuple[0]
            style_doc.setContent(style_qml)
            layer.importNamedStyle(style_doc)
            layer.triggerRepaint()

    def get_streetnames(self) -> list[dict]:
        sql = """SELECT a.FID, a.LABEL_TEXT as LABEL_TEXT
                FROM AX_LAGEBEZOHNEHNR_TBL a
                WHERE (a.SNR = '4107' AND Upper(a.ART) IN ('STRASSE', 'WEG', 'PLATZ'))
                AND a.LZE IS NULL
                ORDER BY LABEL_TEXT asc"""

        return self.select_into_dict_list(sql)

    def get_municipalities(self) -> list[dict]:
        sql = """SELECT a.GEMEINDEKENNZEICHEN as KEY, a.BEZEICHNUNG as VALUE
                FROM AX_GEMEINDE a, (
                        SELECT DISTINCT(SUBSTR(VERSCHLUESSELT, 1, (SELECT MAX(LENGTH(GEMEINDEKENNZEICHEN)) FROM AX_GEMEINDE))) as KEY
                        FROM AX_LAGEBEZEICHNUNGMITHNR
                        WHERE LZE IS NULL
                        ) b
                    WHERE a.GEMEINDEKENNZEICHEN = b.KEY and a.LZE is NULL
                ORDER BY a.BEZEICHNUNG ASC"""

        return self.select_into_dict_list(sql)

    def get_streets(self, municipality_id: str) -> list[dict]:
        sql = """SELECT a.FID, a.SCHLUESSEL as KEY, a.BEZEICHNUNG as VALUE
                FROM AX_LAGEBEZKATEINTRAG a
                   LEFT JOIN AX_LAGEBEZEICHNUNGMITHNR b ON (b.VERSCHLUESSELT = a.SCHLUESSEL)
                WHERE SCHLUESSEL LIKE '{municipality_id}%'
                AND a.LZE IS NULL
                AND b.LZE IS NULL
                GROUP BY a.FID, a.SCHLUESSEL, a.BEZEICHNUNG
                HAVING count(b.FID) > 0
                ORDER BY VALUE ASC"""

        sql = sql.format(municipality_id=municipality_id)
        return self.select_into_dict_list(sql)

    def get_numbers(self, street_key: str) -> list[dict]:
        sql = """SELECT GEB.FID as KEY, HN.VALUE as VALUE
                FROM (
                   SELECT ID as KEY, HAUSNUMMER as VALUE
                   FROM	AX_LAGEBEZEICHNUNGMITHNR
                   WHERE VERSCHLUESSELT = '{street_key}'
                   AND LZE IS NULL
                ) HN
                LEFT JOIN ME_BZ BEZ ON UPPER(BEZ.TABELLE) = Upper('AX_Gebaeude') AND BEZ.ZID=HN.KEY
                JOIN AX_GEBAEUDE GEB ON BEZ.ID=GEB.ID
                ORDER BY VALUE"""

        sql = sql.format(street_key=street_key)
        return self.select_into_dict_list(sql)

    def get_bundesland(self) -> Any:
        """Returns first distinct Bundesland used in table 'ax_flurstueck'."""

        sql = """select distinct(substr(gemarkung, 1, 2)) as bl from ax_flurstueck where lze is null"""
        result = self.select_into_dict_list(sql)
        if not result:
            return ""
        return result[0].get("bl", "")

    def get_gemarkungen(self) -> list[dict]:
        sql = """SELECT a.FID, a.SCHLUESSEL, a.BEZEICHNUNG as BEZEICHNUNG , count(b.FID) AS NUM
                FROM AX_GEMARKUNG a
                LEFT JOIN AX_FLURSTUECK b ON (b.GEMARKUNG = a.SCHLUESSEL)
                WHERE a.LZE IS NULL
                AND b.LZE IS NULL
                GROUP BY a.FID, a.SCHLUESSEL, a.BEZEICHNUNG
                HAVING count(b.FID) > 0
                ORDER BY a.BEZEICHNUNG ASC"""

        return self.select_into_dict_list(sql)

    def search_flurstuecke(self, fsk="", gmk_gmn="", fln="", fsn_zae="", fsn_nen="") -> list[dict]:
        sql = """SELECT FID,
        (ifnull(gemarkung, '')  || '-' || ifnull(flurnummer, '')  || '-' || ifnull(flurstuecksnummer_zaehler, '')  || '-' || ifnull(flurstuecksnummer_nenner, ''))  AS CAPTION
        FROM AX_FLURSTUECK WHERE LZE IS NULL"""

        def add_condition(sql_: str, column: str, value: str) -> str:
            if not value:
                return sql_

            sql_ += f" AND {column} = '{value}'"
            return sql_

        if fsk:
            sql += f" AND flurstueckskennzeichen LIKE '%{fsk}%'"
        else:
            sql = add_condition(sql, "gemarkung", gmk_gmn)
            sql = add_condition(sql, "flurnummer", fln)
            sql = add_condition(sql, "flurstuecksnummer_zaehler", fsn_zae)
            sql = add_condition(sql, "flurstuecksnummer_nenner", fsn_nen)

        sql += " ORDER BY flurstueckskennzeichen"

        return self.select_into_dict_list(sql)

    def get_standard_crs(self):
        """Gets the standard CRS to be used as subset filter.
        ID is used as subset filter and a QgsCoordinateReferenceSystem as fallback for layers with invalid CRS."""

        srids = {
            "ETRS89_UTM32": 25832,
            "ETRS89_UTM33": 25833,
        }

        sql = "SELECT ID, crs FROM ME_KOORDINATEnANGABEN WHERE standard = 1 LIMIT 1"
        result = self.select_into_dict_list(sql)

        self.standard_srs_id = result[0].get("ID") if result else None

        srid = srids.get(result[0].get("crs")) if result else None
        self.standard_crs = QgsCoordinateReferenceSystem(srid)
