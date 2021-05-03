# This Python file uses the following encoding: utf-8
import math
import os

from PySide2.QtWidgets import QMainWindow, QFileDialog
from PySide2.QtCore import QFile, Slot
from PySide2.QtUiTools import QUiLoader


def freq_to_text(value):
    if value >= 1000:
        return f'{round(value/1000, 1)} kHz'

    return f'{round(value, 1)} Hz'


class NewProjectView(QMainWindow):

    def __init__(self, model, controller):
        super(NewProjectView, self).__init__()
        self._model = model
        self._controller = controller

        self.load_ui()
        self.connect_to_controller()
        self.connect_to_model()
        self.set_default_values()

    def open(self):
        self.window.show()

    def close(self):
        self.window.hide()

    def load_ui(self):
        loader = QUiLoader()
        path = os.path.join('designer', "new_project.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file)
        ui_file.close()

    def connect_to_controller(self):
        self.window.line_project_name.textChanged.connect(
            self._controller.change_project_name)
        self.window.line_project_location.textChanged.connect(
            self._controller.change_project_location)
        self.window.open_location.clicked.connect(self.open_location_dialog)
        self.window.cb_audio_driver.currentIndexChanged.connect(
            self._controller.change_audio_driver)
        self.window.cb_audio_device.currentIndexChanged.connect(
            self._controller.change_audio_device)
        self.window.but_create.clicked.connect(
            self._controller.create_new_project)
        self.window.cb_video_devices.currentIndexChanged.connect(
            self._controller.change_video_device)
        self.window.low_freq_dial.valueChanged.connect(
            self._controller.change_low_freq)
        self.window.high_freq_dial.valueChanged.connect(
            self._controller.change_high_freq)

    def connect_to_model(self):
        self._model.project_name_changed.connect(self.on_project_name_changed)
        self._model.project_location_changed.connect(
            self.on_project_location_changed)
        self._model.audio_drivers_set.connect(self.on_audio_drivers_set)
        self._model.audio_driver_changed.connect(self.on_audio_driver_changed)
        self._model.audio_devices_set.connect(self.on_audio_devices_set)
        self._model.audio_device_changed.connect(self.on_audio_device_changed)
        self._model.video_devices_set.connect(self.on_video_devices_set)
        self._model.video_device_changed.connect(self.on_video_device_changed)
        self._model.low_freq_changed.connect(self.on_low_freq_changed)
        self._model.high_freq_changed.connect(self.on_high_freq_changed)
        self._model.low_freq_forced.connect(self.on_low_freq_forced)
        self._model.high_freq_forced.connect(self.on_high_freq_forced)

    def set_default_values(self):
        self._controller.change_project_location(os.path.expanduser("~"))
        self._controller.change_project_name('New Project')
        self._controller.set_audio_drivers()
        self._controller.set_video_devices()
        self.window.high_freq_dial.setValue(1000)
        self.window.low_freq_dial.setValue(40)

    def open_location_dialog(self):
        _dir = str(QFileDialog.getExistingDirectory(
            self, "Choose a location.", str(self._model.project_location)))
        self._controller.change_project_location(_dir)

    @Slot(str)
    def on_project_name_changed(self, value):
        self.window.line_project_name.setText(value)

    @Slot(str)
    def on_project_location_changed(self, value):
        self.window.line_project_location.setText(value)

    @Slot(object)
    def on_audio_drivers_set(self, value):
        # driver_names = [*value]  # Unpacking dict keys
        names = [v['name'] for v in value]
        self.window.cb_audio_driver.clear()
        self.window.cb_audio_driver.addItems(names)

    @Slot(int)
    def on_audio_driver_changed(self, value):
        self._controller.set_audio_devices(value)

    @Slot(object)
    def on_audio_devices_set(self, value):
        self.window.cb_audio_device.clear()
        self.window.cb_audio_device.addItems(value)

    @Slot(int)
    def on_audio_device_changed(self, value):
        print(f'[VIEW]: Audio Device changed: {value}')

    @Slot(object)
    def on_video_devices_set(self, value):
        self.window.cb_video_devices.clear()
        self.window.cb_video_devices.addItems(list(value.values()))

    @Slot(int)
    def on_video_device_changed(self, value):
        print(f'[VIEW]: Video Device changed: {value}')

    @Slot(int)
    def on_low_freq_changed(self, value):

        self.window.low_freq_label.setText(freq_to_text(value))

    @Slot(int)
    def on_high_freq_changed(self, value):
        self.window.high_freq_label.setText(freq_to_text(value))

    @Slot(int)
    def on_low_freq_forced(self, value):
        self.window.low_freq_dial.setValue(math.floor(math.log(value))*10-1)

    @Slot(int)
    def on_high_freq_forced(self, value):
        self.window.high_freq_dial.setValue(math.ceil(math.log(value))*10+1)
