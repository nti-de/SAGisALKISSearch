from typing import Any

from PyQt5.QtXml import QDomDocument
from qgis.core import QgsDataSourceUri, QgsMapLayer, QgsProject, QgsVectorLayer

from .alkisdatasource import AlkisDataSourceSqlite, AlkisDataSourceType, TableInfo


class SqliteSagisConverter(AlkisDataSourceSqlite):
    def __init__(self, uri: QgsDataSourceUri):
        super().__init__(uri)

        # AlkisDataSource
        self.f_class_name = "AX_FLURSTUECK"
        self.datasource_type = AlkisDataSourceType.SAGisSqlite
        self.config_file = "resources/config/GenericDialog/Configuration/AX_FLURSTUECK_SQLITE.xml"
        self.flurstueck_primary_key = "fid"

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

    def add_layers(self) -> None:
        super().add_layers()

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

        uri = f"{self.uri.database()}|layername={table.table_name}"

        if table.type:
            uri += f"|geometrytype={table.type}"

        layer = QgsVectorLayer(uri, table.table_name, "ogr")
        layer.setName(table.caption)

        if table.display_expression:
            layer.setDisplayExpression(table.display_expression)

        layer.setFlags(layer.flags() & ~QgsMapLayer.Removable)
        QgsProject.instance().addMapLayer(layer, addToLegend=False)
        self.group_basemap.insertLayer(0, layer)

        # Load style. Does not happen automatically.
        self.load_style(table, layer)

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
                ORDER BY LABEL_TEXT asc"""

        return self.select_into_dict_list(sql, self.database)

    def get_municipalities(self) -> list[dict]:
        sql = """SELECT a.GEMEINDEKENNZEICHEN as KEY, a.BEZEICHNUNG as VALUE
                FROM AX_GEMEINDE a, (
                        SELECT DISTINCT(SUBSTR(VERSCHLUESSELT, 1, (SELECT MAX(LENGTH(GEMEINDEKENNZEICHEN)) FROM AX_GEMEINDE))) as KEY
                        FROM AX_LAGEBEZEICHNUNGMITHNR
                        ) b
                    WHERE a.GEMEINDEKENNZEICHEN = b.KEY and a.LZE is NULL
                ORDER BY a.BEZEICHNUNG ASC"""

        return self.select_into_dict_list(sql, self.database)

    def get_streets(self, municipality_id: int) -> list[dict]:
        sql = f"""SELECT a.FID, a.SCHLUESSEL as KEY, a.BEZEICHNUNG as VALUE
                FROM AX_LAGEBEZKATEINTRAG a
                   LEFT JOIN AX_LAGEBEZEICHNUNGMITHNR b ON (b.VERSCHLUESSELT = a.SCHLUESSEL)
                WHERE SCHLUESSEL LIKE '{municipality_id}%'
                GROUP BY a.FID, a.SCHLUESSEL, a.BEZEICHNUNG
                HAVING count(b.FID) > 0
                ORDER BY VALUE ASC"""

        return self.select_into_dict_list(sql, self.database)

    def get_numbers(self, street_key: str) -> list[dict]:
        sql = f"""SELECT GEB.FID as KEY, HN.VALUE as VALUE
                FROM (
                   SELECT	ID as KEY, HAUSNUMMER as VALUE
                   FROM	AX_LAGEBEZEICHNUNGMITHNR
                   WHERE 	VERSCHLUESSELT='{street_key}'
                ) HN
                LEFT JOIN ME_BZ BEZ ON UPPER(BEZ.TABELLE) = Upper('AX_Gebaeude') AND BEZ.ZID=HN.KEY
                JOIN AX_GEBAEUDE GEB ON BEZ.ID=GEB.ID
                ORDER BY VALUE"""

        return self.select_into_dict_list(sql, self.database)

    def get_bundesland(self) -> Any:
        """Returns first distinct Bundesland used in table 'ax_flurstueck'."""

        sql = """select distinct(substr(gemarkung, 1, 2)) as bl from ax_flurstueck"""
        result = self.select_into_dict_list(sql, self.database)
        if not result:
            return ""
        return result[0].get("bl", "")

    def get_gemarkungen(self) -> list[dict]:
        sql = """SELECT a.FID, a.SCHLUESSEL, a.BEZEICHNUNG as BEZEICHNUNG , count(b.FID) AS NUM
                FROM AX_GEMARKUNG a
                LEFT JOIN AX_FLURSTUECK b ON (b.GEMARKUNG = a.SCHLUESSEL)
                GROUP BY a.FID, a.SCHLUESSEL, a.BEZEICHNUNG
                HAVING count(b.FID) > 0
                ORDER BY a.BEZEICHNUNG ASC"""

        return self.select_into_dict_list(sql, self.database)

    def search_flurstuecke(self, fsk="", gmk_gmn="", fln="", fsn_zae="", fsn_nen="") -> list[dict]:
        sql = """SELECT FID,
        (ifnull(gemarkung, '')  || '-' || ifnull(flurnummer, '')  || '-' || ifnull(flurstuecksnummer_zaehler, '')  || '-' || ifnull(flurstuecksnummer_nenner, ''))  AS CAPTION
        FROM AX_FLURSTUECK"""

        if fsk:
            sql += f" WHERE flurstueckskennzeichen LIKE '{fsk}'"
            return self.select_into_dict_list(sql, self.database)

        def add_condition(sql_: str, column: str, value: str, is_first: bool):
            if not value:
                return sql_, is_first

            sql_ += " WHERE " if is_first else " AND "
            sql_ += f"{column} = '{value}'"
            return sql_, False

        sql, first = add_condition(sql, "gemarkung", gmk_gmn, True)
        sql, first = add_condition(sql, "flurnummer", fln, first)
        sql, first = add_condition(sql, "flurstuecksnummer_zaehler", fsn_zae, first)
        sql, first = add_condition(sql, "flurstuecksnummer_nenner", fsn_nen, first)

        sql += " ORDER BY flurstueckskennzeichen"

        return self.select_into_dict_list(sql, self.database)
