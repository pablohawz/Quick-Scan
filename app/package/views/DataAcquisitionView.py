# This Python file uses the following encoding: utf-8
import numpy as np
import cv2
import os
import queue

from PySide2.QtWidgets import QMainWindow
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtCore import QEvent, QThread, Slot

from ..services.CameraThread import CameraThread
from ..services.MicWorker import MicWorker
from ..models.ActualProjectModel import ActualProjectModel
from ..services import file as fileutils
from ..services.dsp import get_time_of_recording
from ..services.imbasic import resize

from ..controllers.DataAcquisitionController import DataAcquisitionController
from ..models.DataAcquisitionModel import DataAcquisitionModel

from ..ui.DataAcquisition_ui import Ui_MainWindow as DataAcquisition_ui


def log(msg: str) -> None:
    print(f'[DataAcquisition/View] {msg}')


class DataAcquisitionView(QMainWindow, DataAcquisition_ui):

    def __init__(self,
                 model: DataAcquisitionModel,
                 controller: DataAcquisitionController,
                 parent=None):
        super(DataAcquisitionView, self).__init__(parent)
        self._model = model
        self._controller = controller

        self.setupUi(self)
        self.connect_to_controller()
        self.connect_to_model()
        self.set_default_values()
        self.installEventFilter(self)

    # region ------------------------ QMainWindow ------------------------

    def open(self):
        self.show()

        # Clear state and initial setup
        self.set_default_values()

        # Create and start threads
        self.create_threads()
        min_time = get_time_of_recording(ActualProjectModel.low_freq)
        self._controller.start_cam_thread(min_time)
        self._controller.start_mic_thread()

        # Setup camera thread
        self._controller.change_rows(2)
        self._controller.change_cols(4)
        self._controller.change_padding(40)

    def close(self):
        self.stop_threads()
        self.hide()

    def eventFilter(self, obj, event):
        if obj is self and event.type() == QEvent.Close:
            self.stop_threads()
            event.accept()
            return True
        else:
            return super(DataAcquisitionView, self).eventFilter(obj, event)

    def connect_to_controller(self):
        self.start_stop_button.clicked.connect(
            self._controller.toogle_recording)
        self.rows_sb.valueChanged.connect(self._controller.change_rows)
        self.cols_sb.valueChanged.connect(self._controller.change_cols)
        self.pad_sb.valueChanged.connect(self._controller.change_padding)
        self.capture_bt.clicked.connect(self._controller.take_bg_picture)
        self.go_back_button.clicked.connect(self.go_back)

    def connect_to_model(self):
        self._model.on_mic_thread_running_changed.connect(
            self.handle_mic_thread_running_changed)
        self._model.on_cam_thread_running_changed.connect(
            self.handle_cam_thread_running_changed)
        self._model.on_mic_recording_changed.connect(
            self.handle_mic_recording_changed)
        self._model.on_cam_recording_changed.connect(
            self.handle_cam_recording_changed)
        self._model.on_rows_changed.connect(self.handle_rows_changed)
        self._model.on_cols_changed.connect(self.handle_cols_changed)
        self._model.on_padding_changed.connect(self.handle_padding_changed)
        self._model.on_bg_img_changed.connect(self.handle_bg_img_changed)

    def set_default_values(self):
        title = 'Quick Scan: Data acquisition'
        self.setWindowTitle(title)
        self.q = queue.Queue()
        self._model.clear_state()
        self._img_saved = False
        self.start_stop_button.setDisabled(False)
        self.start_stop_button.setText('Start!')

    def go_back(self):
        log('Going back!')

        self._controller.stop_cam_thread()
        self._controller.stop_mic_thread()

        self._controller.navigate('new_project')

    # endregion

    # region -------------------------- Threads --------------------------

    def create_threads(self):
        # 1. Start camera Thread
        self._model.camThread = CameraThread(self)
        self._model.camThread.update_frame.connect(self.handle_new_image)
        self._model.camThread.on_stop_recording.connect(self.save_positon_data)
        self._model.camThread.on_camera_caracteristics_detected.connect(
            self.save_camera_characteristica)
        self._model.camThread.on_handle_all_regions_rec.connect(
            self.handle_all_regions_rec)

        # 2. Create Mic Thread
        micWorker = MicWorker()
        micThread = QThread()
        micWorker.moveToThread(micThread)

        micWorker.config_mic(ActualProjectModel.audio_device_index)
        micThread.started.connect(micWorker.run)

        micWorker.update_volume.connect(self.handle_new_audio)
        micWorker.finished.connect(self.handle_rec_ended)

        micWorker.finished.connect(micThread.quit)
        micWorker.finished.connect(micWorker.deleteLater)
        micThread.finished.connect(micThread.deleteLater)

        self._model.micWorker = micWorker
        self._model.micThread = micThread

    def stop_threads(self):
        self._controller.stop_mic_thread()
        self._controller.stop_cam_thread()

    # endregion

    # region ------------------------- Handlers --------------------------

    @Slot(bool)
    def handle_rec_ended(self, error: bool):
        if error:
            return

        self._controller.navigate('display_results')

    @ Slot(bool)
    def handle_mic_thread_running_changed(self, value):
        pass

    @ Slot(bool)
    def handle_cam_thread_running_changed(self, value):
        pass

    @ Slot(object)
    def save_positon_data(self, value):
        ActualProjectModel.data_x = value["x_data"]
        ActualProjectModel.data_y = value["y_data"]
        ActualProjectModel.grid = self._model.get_grid_as_list()

        # Write data to disk
        path = os.path.join(ActualProjectModel.project_location,
                            'Position Data')
        fileutils.mkdir(path)

        fileutils.save_np_to_txt(value["x_data"], path, file_name="data.x")
        fileutils.save_np_to_txt(value["y_data"], path, file_name="data.y")
        fileutils.save_np_to_txt(
            self._model.get_grid_as_list(), path, file_name='grid.config')

    def handle_mic_recording_changed(self, rec):
        if rec:
            self.start_stop_button.setDisabled(True)
            self.start_stop_button.setText('Stop recording')
        else:
            self.start_stop_button.setText('Start!')

    def handle_cam_recording_changed(self, rec):
        pass

    @Slot()
    def handle_all_regions_rec(self):
        self.start_stop_button.setDisabled(False)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_format = QImage(
            rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(qt_format)

    @Slot(np.ndarray)
    def handle_new_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        if self._model.camThread is None:
            return

        width = self.frameGeometry().width() * 0.8
        if width > 1000:
            width = 1000

        small_img = resize(cv_img, width=int(width))

        img_w_grid = self._model.camThread._grid.draw_grid(
            small_img, thickness=2)
        qt_img = self.convert_cv_qt(img_w_grid)

        self.cam_view.setPixmap(qt_img)

    @ Slot(int)
    def handle_new_audio(self, value):
        # self.q.put(value)
        pass

    @ Slot(tuple)
    def save_camera_characteristica(self, value: tuple) -> None:
        print('[Data Acquisition] Saving camera characteristics to disk...')
        print(f'Value: {value}')
        array = np.array(value, dtype=object)

        path = os.path.join(ActualProjectModel.project_location,
                            'Position Data')
        fileutils.save_np_to_txt(
            array, path, file_name='camera.data')

    @Slot(float)
    def handle_rows_changed(self, value):
        self.rows_sb.setValue(value)

    @Slot(float)
    def handle_cols_changed(self, value):
        self.cols_sb.setValue(value)

    @Slot(float)
    def handle_padding_changed(self, value):
        self.pad_sb.setValue(value)

    @Slot(np.ndarray)
    def handle_bg_img_changed(self, img: np.ndarray) -> None:
        dirpath = os.path.join(
            ActualProjectModel.project_location, 'Images')
        fileutils.mkdir(dirpath)
        filename = os.path.join(dirpath, 'bg.png')

        log(f'Saving image in {filename}')
        log(f'Img shape = {img.shape}')
        cv2.imwrite(filename, img)
        self._img_saved = True

    # endregion
