import os

PLUGIN_NAME = "SAGis ALKIS Suche"
VERSION = "1.0.1"
DEPENDENCIES = [
    "pandas",
    "xlsxwriter",
    "xsdata"
]


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SagisAlkisSearchPlugin class from file sagisalkissearchplugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """

    from .sagisplugin import dependencies
    bundled_packages = os.path.join(os.path.dirname(__file__), "bundled")
    dependency_check = dependencies.check_packages(DEPENDENCIES, plugin_name=PLUGIN_NAME, plugin_path=bundled_packages)
    if not dependency_check:
        # Create anonymous object so that QGIS can call initGui and unload without crashing.
        return type('', (object,), {"initGui": (lambda self: None), "unload": (lambda self: None)})()

    from .sagisalkissearchplugin import SagisAlkisSearchPlugin
    return SagisAlkisSearchPlugin(iface)
