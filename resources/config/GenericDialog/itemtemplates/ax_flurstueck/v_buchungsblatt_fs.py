from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QFormLayout

from ...... import commonfunctions
from ......resultdialog.dialogbindingwidget import DialogBindingWidget
from ......resultdialog.dialogitem import DialogItem
from ......sagisgndlgconfig.configcontext import ConfigContext
from ......sagisgndlgconfig.sagis_gn_dlg_config import SagisGnDlgConfig


class V_BUCHUNGSBLATT_FS(DialogItem):
    def __init__(self, context: ConfigContext,
                 panel: SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel,
                 data: dict, object_index=-1, total_objects=0, parent=None):
        super().__init__(context, panel, data, object_index, total_objects, parent)

        self.labelBuchungsblattKennz = QLabel()
        self.labelBuchungsblattbezirk = QLabel()
        self.labelBuchungsblattnummer = QLabel()
        self.labelBlattart = QLabel()

        self.setLayout(QFormLayout())
        self.layout().setHorizontalSpacing(64)

        self.layout().addRow("Buchungsblattkennz.:", self.labelBuchungsblattKennz)
        self.layout().addRow("Buchungsblattbezirk:", self.labelBuchungsblattbezirk)
        self.layout().addRow("Buchungsblattnummer:", self.labelBuchungsblattnummer)
        self.layout().addRow("Blattart:", self.labelBlattart)

        for i in range(self.layout().rowCount()):
            item = self.layout().itemAt(i, QFormLayout.LabelRole)
            if item:
                label = item.widget()
                font = label.font()
                font.setBold(True)
                item.widget().setFont(font)

            item = self.layout().itemAt(i, QFormLayout.FieldRole)
            if item and isinstance(item.widget(), QLabel):
                item.widget().setTextInteractionFlags(item.widget().textInteractionFlags() | Qt.TextSelectableByMouse)

        # Bindings
        self.gv_BESCHRIEBDERRECHTSGEMEINSC = DialogBindingWidget()
        self.gv_AX_BUCHUNGSSTELLE = DialogBindingWidget()

        self.layout().addRow(self.gv_BESCHRIEBDERRECHTSGEMEINSC)
        self.layout().addRow(self.gv_AX_BUCHUNGSSTELLE)

    def set_label_texts(self):
        self.labelBuchungsblattKennz.setText(
            f"{self.get_value('buchungsblattkennzeichen')}"
        )

        self.labelBuchungsblattbezirk.setText(
            f"{self.get_value('bb_bezirk_key')}/{self.get_value('bb_bezirk_value')}"
        )

        self.labelBuchungsblattnummer.setText(
            f"{self.get_value('buchungsblattnummermitbuch')}"
        )

        self.labelBlattart.setText(
            f"{self.get_value('blattart')} - {self.get_value('blattart_value')}"
        )
