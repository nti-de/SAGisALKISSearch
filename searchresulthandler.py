from typing import Union, Optional

from qgis.core import Qgis, QgsExpression, QgsFeature, QgsFeatureRequest, QgsProject, QgsVectorLayer
from qgis.utils import iface

PROJECT_ENTRY_SCOPE = "sagis_alkis_search"


def street_search(result_id: int) -> None:
    layer_id, ok = QgsProject.instance().readEntry(PROJECT_ENTRY_SCOPE, "street_result_layer")
    layer = None
    if ok:
        layer = QgsProject.instance().mapLayer(layer_id)
    if not layer:
        iface.messageBar().pushMessage(title="SAGis ALKIS Suche",
                                       text="Beschriftungslayer existiert nicht",
                                       level=Qgis.MessageLevel.Warning,
                                       duration=5)
        return
    highlight_result(layer, result_id)


def building_search(result_id: int) -> None:
    layer_id, ok = QgsProject.instance().readEntry(PROJECT_ENTRY_SCOPE, "building_result_layer")
    layer = None
    if ok:
        layer = QgsProject.instance().mapLayer(layer_id)
    if not layer:
        iface.messageBar().pushMessage(title="SAGis ALKIS Suche",
                                       text="Gebäudelayer existiert nicht",
                                       level=Qgis.MessageLevel.Warning,
                                       duration=5)
        return
    highlight_result(layer, result_id)


def get_features(layer: QgsVectorLayer, key_value: Union[int, str, list]) -> list[QgsFeature]:
    if not layer:
        return []

    p_key = layer.primaryKeyAttributes()[0]

    if isinstance(key_value, list):
        values = ", ".join([f"'{v}'" for v in key_value])
        expression = f"\"{layer.fields().field(p_key).name()}\" IN ({values})"
    else:
        expression = f"\"{layer.fields().field(p_key).name()}\" = '{key_value}'"
    return list(layer.getFeatures(QgsFeatureRequest(QgsExpression(expression))))


def get_feature_ids(layer: QgsVectorLayer, key_value: Union[int, str, list]) -> list[int]:
    features = get_features(layer, key_value)
    return [f.id() for f in features]


def highlight_result(layer: QgsVectorLayer, key_value: Union[int, str, list]):
    feature_ids = get_feature_ids(layer, key_value)
    iface.mapCanvas().zoomToFeatureIds(layer, feature_ids)
    iface.mapCanvas().flashFeatureIds(layer, feature_ids)


def flurstueck_search(primary_key_values: list[int]) -> Optional[QgsVectorLayer]:
    if not primary_key_values:
        return

    layer_id, ok = QgsProject.instance().readEntry(PROJECT_ENTRY_SCOPE, "flurstueck_result_layer")
    layer = None
    if ok:
        layer: QgsVectorLayer = QgsProject.instance().mapLayer(layer_id)
    if not layer:
        iface.messageBar().pushMessage(title="SAGis ALKIS Suche",
                                       text="Flurstücklayer existiert nicht",
                                       level=Qgis.MessageLevel.Info,
                                       duration=5)
        return None

    # Zoom, flash and select
    feature_ids = get_feature_ids(layer, primary_key_values)
    iface.mapCanvas().zoomToFeatureIds(layer, feature_ids)
    iface.mapCanvas().flashFeatureIds(layer, feature_ids)
    layer.selectByIds(feature_ids, behavior=Qgis.SelectBehavior.SetSelection)

    return layer


def unselect_flurstuecke():
    layer_id, ok = QgsProject.instance().readEntry(PROJECT_ENTRY_SCOPE, "flurstueck_result_layer")
    layer = None
    if ok:
        layer = QgsProject.instance().mapLayer(layer_id)
    if not layer:
        iface.messageBar().pushMessage(title="SAGis ALKIS Suche",
                                       text="Flurstücklayer existiert nicht",
                                       level=Qgis.MessageLevel.Warning,
                                       duration=5)
        return
    layer.removeSelection()
