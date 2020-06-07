from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainterPath, QPainter
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets, QtCore, QtGui

from shape import Shape

CURSOR_DEFAULT = QtCore.Qt.ArrowCursor
CURSOR_POINT = QtCore.Qt.PointingHandCursor
CURSOR_DRAW = QtCore.Qt.CrossCursor
CURSOR_MOVE = QtCore.Qt.ClosedHandCursor

CREATE, EDIT = 0, 1

# clCURSOR_GRAB = QtCore.Qt.OpenHandCursorass


class Canvas(QtWidgets.QWidget):
    centerChanged = QtCore.pyqtSignal(QtCore.QPointF)
    zoomChanged = QtCore.pyqtSignal(float)
    image_wapper = None
    scale = 1.0
    main_win = None

    mode = CREATE

    def __init__(self, parent):
        super(Canvas, self).__init__(parent)
        self.main_win = parent
        self._curCursor = CURSOR_DEFAULT
        self.shapes = []
        self.cur_shape = None
        self._Painter = QtGui.QPainter()

        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.WheelFocus)

    def setDrawMode(self, draw_mode):
        Canvas._drawMode = draw_mode

    def setMode(self, mode):
        Canvas.mode = mode

    def drawing(self):
        return Canvas.mode == CREATE

    def editing(self):
        return Canvas.mode == EDIT

    def wheelEvent(self, ev: QtGui.QWheelEvent):
        if not self.pixmap():
            return
        mods = ev.modifiers()
        delta = ev.angleDelta()
        if int(mods) != QtCore.Qt.ControlModifier:
            scale = self.scale
            if delta.y() > 0:
                scale *= 1.1
            else:
                scale *= 0.9

            self.zoomChanged.emit(scale)
        else:
            self.centerChanged.emit(delta)

    def mouseMoveEvent(self, ev):
        if not self.pixmap():
            return
        pos = self.transformPos(ev.localPos())

    def mousePressEvent(self, ev):
        if not self.pixmap():
            return
        pos = self.transformPos(ev.localPos())
        self._curPos = pos
        self.main_win.showStatusTips(
            "world pos: [{0},{1}]".format(pos.x(), pos.y()))

        if ev.button() == Qt.LeftButton:

            if self.cur_shape:
                self.cur_shape.addPoint(pos)
            else:
                self.cur_shape = Shape(shape_type=Canvas._drawMode)

                self.cur_shape.fill = True
                self.cur_shape.addPoint(pos)
            self.repaint()

    def paintEvent(self, ev):
        # if not self.shapes:
        #     return super(Canvas, self).paintEvent(ev)
        if not self.pixmap():
            return

        p = self._Painter
        p.begin(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.HighQualityAntialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        p.scale(self.scale, self.scale)
        p.translate(self.offsetToCenter())
        # p.setPen(QColor(255, 0, 0))
        p.drawImage(0, 0, self.pixmap())

        for shape in self.shapes:
            shape.paint(p)

        if self.cur_shape:
            self.cur_shape.paint(p)

        p.end()

    def pixmap(self):
        if self.image_wapper:
            return self.image_wapper.getQImage()
        return None

    def outOfPixmap(self, p):
        w, h = self.pixmap().width(), self.pixmap().height()
        return not (0 <= p.x() <= w - 1 and 0 <= p.y() <= h - 1)

    def transformPos(self, point):
        return point / self.scale - self.offsetToCenter()

    def offsetToCenter(self):
        pixmap = self.pixmap()
        s = self.scale
        area = super(Canvas, self).size()
        w, h = pixmap.width() * s, pixmap.height() * s
        aw, ah = area.width(), area.height()
        x = (aw - w) / (2 * s) if aw > w else 0
        y = (ah - h) / (2 * s) if ah > h else 0
        return QtCore.QPoint(x, y)

    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        if self.pixmap():
            return self.scale * self.pixmap().size()

        return super(Canvas, self).minimumSizeHint()

    def leaveEvent(self, ev):
        self.restoreCursor()

    def focusOutEvent(self, ev):
        self.restoreCursor()

    def enterEvent(self, ev):
        self.overrideCursor(self._curCursor)

    def overrideCursor(self, cursor):
        old_cursor = QApplication.overrideCursor()
        if old_cursor == None or old_cursor != cursor:
            QApplication.restoreOverrideCursor()
            QApplication.setOverrideCursor(cursor)
            self._curCursor = cursor

    @staticmethod
    def restoreCursor():
        QApplication.restoreOverrideCursor()
