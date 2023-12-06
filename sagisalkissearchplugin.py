from PyQt5.QtWidgets import QMenu, QToolButton
from qgis.core import QgsProject, QgsVectorLayer
from qgis.utils import iface

import os.path

from . import loggerutils, PLUGIN_NAME
from . import utils
from .resultdialogbuilder import ResultDialogBuilder
from .sagisplugin.sagispluginbase import SagisPluginBase
from .searchdialog import SearchDialog
from .settingsdialog import SettingsDialog


class SagisAlkisSearchPlugin(SagisPluginBase):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        super().__init__(
            iface,
            PLUGIN_NAME,
            "ALKIS Suche"
        )

        # Declare instance attributes
        self.sagis_icon = os.path.abspath(os.path.join(self.plugin_dir, "resources/SAGis_Logo_Search.png"))
        self.dlg = None
        self.tool_button = None
        self.popup_menu = None

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        search_action = self.add_action(
            text="ALKIS Suche...",
            callback=self.run,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False,
            icon_path=self.sagis_icon,
        )

        open_selected_action = self.add_action(
            text="Dialog für Ausgewählte Flurstücke öffnen...",
            callback=self.open_dialog_for_selected,
            add_to_toolbar=False,
            parent=self.iface.mainWindow()
        )

        self.add_action(
            text="Einstellungen...",
            callback=self.open_settings,
            add_to_toolbar=False,
            parent=iface.mainWindow()
        )

        self.popup_menu = QMenu()
        self.popup_menu.addAction(open_selected_action)

        self.tool_button = QToolButton()
        self.tool_button.setDefaultAction(search_action)
        self.tool_button.setMenu(self.popup_menu)
        self.tool_button.setPopupMode(QToolButton.MenuButtonPopup)

        if not self.toolbar:
            self.add_tool_bar()
        self.actions.append(self.toolbar.addWidget(self.tool_button))

        # will be set False in run()
        self.first_start = True

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started

        if self.first_start == True or not isinstance(self.dlg, SearchDialog):
            self.first_start = False
            self.dlg = SearchDialog(self.iface.mainWindow())

        self.dlg.show()
        self.dlg.activateWindow()
        self.dlg.show()

    def open_settings(self):
        dlg = SettingsDialog(self.iface.mainWindow())
        dlg.show()
        dlg.exec_()

    def open_dialog_for_selected(self):
        if not SearchDialog.check_datasource_types():
            return

        project_entry_scope = "sagis_alkis_search"
        layer_id, ok = QgsProject.instance().readEntry(project_entry_scope, "flurstueck_result_layer")
        layer = QgsProject.instance().mapLayer(layer_id) if ok else None
        if not isinstance(layer, QgsVectorLayer):
            iface.messageBar().pushInfo(title="SAGis ALKIS Suche", message="Flurstücklayer existiert nicht",)
            return

        pk_attributes = layer.primaryKeyAttributes()
        if not pk_attributes:
            loggerutils.log_error(f"Fehler:\nKein Primärschlüssel für Layer '{layer.name()}'")
        pk_name = layer.fields().field(pk_attributes[0]).name()

        selected = [{pk_name: f.attribute(pk_name)} for f in layer.selectedFeatures()]
        if not selected:
            self.iface.messageBar().pushInfo(title="SAGis ALKIS Suche", message="Keine Flurstücke ausgewählt")
            return

        datasource = utils.create_datasource()
        if not datasource:
            self.iface.messageBar().pushInfo(title="SAGis ALKIS Suche", message="Keine Datenquelle konfiguriert")
            return

        dlg_builder = ResultDialogBuilder(selected, datasource.f_class_name, pk_name, datasource, datasource.config_file)
        dlg_builder.build()
