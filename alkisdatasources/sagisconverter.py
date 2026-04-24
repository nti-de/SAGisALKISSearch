from typing import Any, List

from qgis.core import QgsAbstractDatabaseProviderConnection, QgsDataSourceUri, QgsProject, QgsVectorLayer, QgsWkbTypes

from .alkisdatasource import AlkisDataSourcePostgres, AlkisDataSourceType, TableInfo
from .. import utils


class SagisConverter(AlkisDataSourcePostgres):
    def __init__(self, connection: QgsAbstractDatabaseProviderConnection):
        super().__init__(connection)

        # AlkisDataSource
        self.f_class_name = "AX_FLURSTUECK"
        self.datasource_type = AlkisDataSourceType.SAGisPgSql
        self.config_file = "resources/config/GenericDialog/Configuration/AX_FLURSTUECK.xml"
        self.flurstueck_primary_key = "fid"

        self.tables = {
            "ax_flurstueck": TableInfo("ax_flurstueck", "Flurstücke", "geom", "fid"),
            "ax_gebaeude": TableInfo("ax_gebaeude", "Gebäude", "geom", "fid", type=QgsWkbTypes.Type.MultiSurface),
            "ax_flurstueck_tbl": TableInfo("ax_flurstueck_tbl", "Beschriftung Flurstück", "geom", "fid"),
            "ax_flurstueck_oa_line": TableInfo("ax_flurstueck_oa", "ALKIS_BB - AX_Flurstueck_oa", "geom", "fid",
                                               type=QgsWkbTypes.Type.LineString),
            "ax_flurstueck_oa_arrowhead": TableInfo("ax_flurstueck_oa", "ALKIS_BB - AX_Flurstueck_oa", "geom", "fid",
                                                    type=QgsWkbTypes.Type.Point),
            "ax_gebaeude_tbl": TableInfo("ax_gebaeude_tbl", "Beschriftung Hausnummer", "geom", "fid",
                                         type=QgsWkbTypes.Type.Point),
            "ax_lagebezohnehnr_tbl": TableInfo("ax_lagebezohnehnr_tbl", "Straßennamen", "geom", "fid")
        }

        self.created_layers: List[QgsVectorLayer] = []

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
        JOIN AX_GEBAEUDE GEB ON BEZ.ID=GEB.ID"""

        sql = sql.format(street_key=street_key)
        return self.select_into_dict_list(sql)

    # Flurstück search
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
        WHERE a.lze IS NULL
        AND b.LZE IS NULL
        GROUP BY a.FID, a.SCHLUESSEL, a.BEZEICHNUNG
        HAVING count(b.FID) > 0
        ORDER BY a.BEZEICHNUNG ASC"""

        return self.select_into_dict_list(sql)

    def search_flurstuecke(self, fsk="", gmk_gmn="", fln="", fsn_zae="", fsn_nen="") -> list[dict]:
        sql = """SELECT
         FID, (
         coalesce(gemarkung, '') || '-' ||
         flurnummer || '-' ||
         coalesce(flurstuecksnummer_zaehler, '') || '-' ||
         coalesce(flurstuecksnummer_nenner, '')
         ) AS CAPTION
        FROM AX_FLURSTUECK
        WHERE LZE IS NULL"""

        def add_condition(sql_: str, column: str, value: str) -> str:
            if not value:
                return sql_

            sql_ += f" AND {column} = '{value}'"
            return sql_

        if fsk:
            sql += f" AND flurstueckskennzeichen LIKE '%{fsk}%'"
            return self.select_into_dict_list(sql)
        else:
            sql = add_condition(sql, "gemarkung", gmk_gmn)
            sql = add_condition(sql, "flurnummer", fln)
            sql = add_condition(sql, "flurstuecksnummer_zaehler", fsn_zae)
            sql = add_condition(sql, "flurstuecksnummer_nenner", fsn_nen)

        sql += " ORDER BY flurstueckskennzeichen"

        return self.select_into_dict_list(sql)

    def add_layers(self) -> None:
        super().add_layers()

        for table in self.tables.values():
            self.add_layer(table)

        self.street_result_layer = self.tables["ax_lagebezohnehnr_tbl"].layer_id
        self.building_result_layer = self.tables["ax_gebaeude"].layer_id
        self.flurstueck_result_layer = self.tables["ax_flurstueck"].layer_id
        self.save_result_layers()

    def add_layer(self, table: TableInfo):
        uri = QgsDataSourceUri(self.connection.uri())
        uri.setDataSource("public", table.table_name, table.geom_column, aKeyColumn=table.primary_key_column)

        if table.type:
            uri.setWkbType(table.type)

        layer = QgsVectorLayer(uri.uri(), table.table_name, "postgres")
        layer.setName(table.caption)
        layer.setSubsetString("LZE IS NULL")

        if not layer.isValid() and self.created_layers:
            layer.setCrs(self.created_layers[0].crs())

        if table.display_expression:
            layer.setDisplayExpression(table.display_expression)

        if self.set_layers_readonly:
            layer.setReadOnly(True)

        if self.set_layers_required:
            utils.set_layer_required(layer, True)

        QgsProject.instance().addMapLayer(layer, addToLegend=False)
        tree_layer = self.group_basemap.insertLayer(0, layer)
        tree_layer.setExpanded(False)

        table.layer_id = layer.id()

        self.created_layers.append(layer)
