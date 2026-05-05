from typing import Union, Optional

from qgis.core import Qgis, QgsApplication, QgsExpression, QgsFeatureIterator, QgsFeatureRequest, QgsProject, QgsVectorLayer
from qgis.utils import iface

from .constants import PROJECT_ENTRY_SCOPE
from .tasks.featureidstask import FeatureIdsTask

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


def get_features(layer: QgsVectorLayer, key_value: Union[int, str, list]) -> Optional[QgsFeatureIterator]:
    if not layer:
        return None

    p_key = layer.primaryKeyAttributes()[0]

    if isinstance(key_value, list):
        values = ", ".join([f"'{v}'" for v in key_value])
        expression = f"\"{layer.fields().field(p_key).name()}\" IN ({values})"
    else:
        expression = f"\"{layer.fields().field(p_key).name()}\" = '{key_value}'"
    it = layer.getFeatures(QgsFeatureRequest(QgsExpression(expression)).setNoAttributes())
    return it


def get_feature_ids(layer: QgsVectorLayer, key_value: Union[int, str, list]) -> list[int]:
    iterator = get_features(layer, key_value)
    if not iterator:
        return []
    result = [f.id() for f in iterator]
    return result


def highlight_result(layer: QgsVectorLayer, key_value: Union[int, str, list]) -> None:
    feature_ids = get_feature_ids(layer, key_value)
    if len(feature_ids) == 1:
        iface.mapCanvas().zoomToFeatureIds(layer, feature_ids)
        iface.mapCanvas().flashFeatureIds(layer, feature_ids)


def flurstueck_search(layer: Optional[QgsVectorLayer], primary_key_values: list[int]) -> None:
    if not primary_key_values:
        return

    if not layer:
        iface.messageBar().pushMessage(title="SAGis ALKIS Suche",
                                       text="Flurstücklayer existiert nicht",
                                       level=Qgis.MessageLevel.Info,
                                       duration=5)
        return

    # Select features
    # Use task instead of get_feature_ids() because of possibly very long list of values.
    task = FeatureIdsTask(layer, primary_key_values)
    task.taskCompleted.connect(
        lambda: layer.selectByIds(task.feature_ids, behavior=Qgis.SelectBehavior.SetSelection)
    )
    QgsApplication.taskManager().addTask(task)


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
