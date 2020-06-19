from qtpy import QtWidgets
from qtpy.QtCore import Qt


class FrameSlider(QtWidgets.QSlider):
    def __init__(self, parent):
        super(FrameSlider, self).__init__(Qt.Horizontal, parent)

    def setValueNoSignal(self, val):
        self.blockSignals(True)
        self.setValue(val)
        self.blockSignals(False)

    def wheelEvent(self, ev):
        pass

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            minimum = self.minimum()
            maximum = self.maximum()
            if self.orientation() == Qt.Vertical:
                self.setValue(minimum + ((maximum-minimum) *
                                         (self.height()-ev.y())) / self.height())
            else:
                self.setValue(minimum + ((maximum-minimum)
                                         * ev.x()) / self.width())

            ev.accept()
        super(FrameSlider, self).mousePressEvent(ev)
