from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QFormLayout

from ...... import commonfunctions
from ......resultdialog.dialogbindingwidget import DialogBindingWidget
from ......resultdialog.dialogitem import DialogItem
from ......sagisgndlgconfig.configcontext import ConfigContext
from ......sagisgndlgconfig.sagis_gn_dlg_config import SagisGnDlgConfig


class V_LAGEBEZEICHNUNG_FS(DialogItem):
    def __init__(self, context: ConfigContext,
                 panel: SagisGnDlgConfig.Container.InfoTemplate.Panels.Panel,
                 data: dict, object_index=-1, total_objects=0, parent=None):
        super().__init__(context, panel, data, object_index, total_objects, parent)

        self.labelKreisRegion = QLabel()
        self.labelGemeinde = QLabel()
        self.labelOrtsteil = QLabel()
        self.labelStrasse = QLabel()
        self.labelHausnummer = QLabel()
        self.labelZusatz = QLabel()

        self.setLayout(QFormLayout())
        self.layout().setHorizontalSpacing(64)

        self.layout().addRow("Kreis / Region:", self.labelKreisRegion)
        self.layout().addRow("Gemeinde:", self.labelGemeinde)
        self.layout().addRow("Ortsteil:", self.labelOrtsteil)
        self.layout().addRow("Strasse:", self.labelStrasse)
        self.layout().addRow("Hausnummer:", self.labelHausnummer)
        self.layout().addRow("Zusatz zur Lagebezeichnung:", self.labelZusatz)

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

    def set_label_texts(self):
        self.labelKreisRegion.setText(
            f"{self.get_value('sqltextkreisregion')}"
        )

        self.labelGemeinde.setText(
            f"{self.get_value('sqltextgemeinde')}"
        )

        self.labelOrtsteil.setText(
            f"{self.get_value('ortsteil')}"
        )

        self.labelStrasse.setText(
            f"{self.get_value('unverschluesselt2') if not self.get_value('unverschluesselt') else self.get_value('unverschluesselt')}"
        )

        self.labelHausnummer.setText(
            f"{self.get_value('hausnummer')}"
        )

        self.labelZusatz.setText(
            f"{self.get_value('zusatzzurlagebezeichnung')}"
        )
