# This Python file uses the following encoding: utf-8
import os
from package.models.ActualProjectModel import ActualProjectModel

from PySide2.QtWidgets import QMainWindow, QFileDialog
from PySide2.QtCore import QFile, Slot
from PySide2.QtUiTools import QUiLoader


class DisplayResultsView(QMainWindow):
    def __init__(self, model, controller):
        super(DisplayResultsView, self).__init__()
        self._model = model
        self._controller = controller

        self.load_ui()
        self.connect_to_controller()
        self.connect_to_model()
        self.set_default_values()

    def open(self):
        self.window.show()
        self.onOpen()

    def close(self):
        self.window.hide()

    def load_ui(self):
        loader = QUiLoader()
        path = os.path.join('designer', "display_results.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file)
        ui_file.close()

    def connect_to_controller(self):
        pass

    def connect_to_model(self):
        self._model.data_x_changed.connect(self.on_data_x_changed)
        self._model.data_y_changed.connect(self.on_data_y_changed)
        pass

    def set_default_values(self):
        pass

    def onOpen(self):
        self._controller.set_data_x(ActualProjectModel.data_x)
        self._controller.set_data_y(ActualProjectModel.data_y)

    def on_data_x_changed(self):
        pass

    def on_data_y_changed(self):
        pass