from typing import Optional

from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QProgressBar
from qgis.core import QgsApplication, QgsTask


class TaskProgressBar(QProgressBar):

    task_started = pyqtSignal()
    task_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 100)
        self.setVisible(False)
        self.setFixedSize(200, 20)
        self._tracked_task_id: Optional[int] = None
        self._manual: bool = False
        self._manager = QgsApplication.taskManager()
        self._manager.progressChanged.connect(self._on_progress_changed)
        self._manager.statusChanged.connect(self._on_status_changed)

    def track(self, task_id: int) -> None:
        self._tracked_task_id = task_id
        self.setValue(0)
        self.setVisible(True)
        self.task_started.emit()

    def begin_manual(self, maximum: int) -> None:
        self._manual = True
        self.setRange(0, maximum)
        self.setValue(0)
        self.setVisible(True)
        self.task_started.emit()

    def update_manual(self, value: int) -> None:
        if self._manual:
            self.setValue(value)

    def end_manual(self) -> None:
        if not self._manual:
            return
        self._manual = False
        self.setRange(0, 100)
        self.setValue(0)
        self.setVisible(False)
        self.task_finished.emit()

    def _on_progress_changed(self, task_id: int, progress: float) -> None:
        if task_id == self._tracked_task_id:
            self.setValue(int(progress))

    def _on_status_changed(self, task_id: int, status: int) -> None:
        if task_id != self._tracked_task_id:
            return

        if status in (QgsTask.TaskStatus.Complete, QgsTask.TaskStatus.Terminated):
            self._tracked_task_id = None
            self.setVisible(False)
            self.setValue(0)
            self.task_finished.emit()

    def is_tracking(self) -> bool:
        return self._tracked_task_id is not None or self._manual
