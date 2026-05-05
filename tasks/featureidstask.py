from qgis.core import QgsExpression, QgsFeatureIterator, QgsFeatureRequest, QgsTask, QgsVectorLayer


class FeatureIdsTask(QgsTask):

    def __init__(self, layer: QgsVectorLayer, primary_key_values: list[int]) -> None:
        super().__init__("Feature-Ids ermitteln")
        self._layer = layer
        self._primary_key_values = primary_key_values
        self.feature_ids: list[int] = []

    def run(self) -> bool:
        iterator = self._get_feature_iterator()
        if not iterator:
            return False
        self.feature_ids = [f.id() for f in iterator]
        return not self.isCanceled()

    def _get_feature_iterator(self) -> QgsFeatureIterator | None:
        if not self._layer:
            return None

        p_key = self._layer.primaryKeyAttributes()[0]
        values = ", ".join([f"'{v}'" for v in self._primary_key_values])
        expression = f"\"{self._layer.fields().field(p_key).name()}\" IN ({values})"

        it = self._layer.getFeatures(QgsFeatureRequest(QgsExpression(expression)).setNoAttributes())
        return it
