from PySide2.QtCore import QObject, Signal


class Navigator(QObject):

    navigator = Signal(str)

    def __init__(self):
        super().__init__()

    # @Slot(str)
    def navigate(self, value):
        print(f'[Navigator] navigate -> {value}')
        self.navigator.emit(value)
