from typing import Any

from qgis.core import QgsTask

from ..alkisdatasources.alkisdatasource import AlkisDataSource


class FlurstueckSearchTask(QgsTask):

    def __init__(self, datasource: AlkisDataSource, fsk="", gmk_gmn="", fln="", fsn_zae="", fsn_nen=""):
        super().__init__("Flurstücksuche")
        self.datasource = datasource
        self.fsk = fsk
        self.gmk_gmn = gmk_gmn
        self.fln_fln = fln
        self.fsn_zae = fsn_zae
        self.fsn_nen = fsn_nen
        self.results: list[dict[str, Any]] = []

    def run(self) -> bool:
        self.results = self.datasource.search_flurstuecke(
            self.fsk, self.gmk_gmn, self.fln_fln, self.fsn_zae, self.fsn_nen)
        return not self.isCanceled()
