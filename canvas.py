from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainterPath, QPainter
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets, QtCore, QtGui

from shape import Shape

CURSOR_DEFAULT = QtCore.Qt.ArrowCursor
CURSOR_POINT = QtCore.Qt.PointingHandCursor
CURSOR_DRAW = QtCore.Qt.CrossCursor
CURSOR_MOVE = QtCore.Qt.ClosedHandCursor


# clCURSOR_GRAB = QtCore.Qt.OpenHandCursorass


class Canvas(QtWidgets.QWidget):

    image_wapper = None
    scale = 1
    main_win = None

    def __init__(self, parent):
        super(Canvas, self).__init__()
        self.main_win = parent
        self._curCursor = CURSOR_DEFAULT
        self.shapes = []
        self.cur_shape = None
        self._Painter = QtGui.QPainter()

        self.setMouseTracking(True)

    def mouseMoveEvent(self, ev):
        self.overrideCursor(CURSOR_DRAW)

    def mousePressEvent(self, ev):
        pos = self.transformPos(ev.localPos())
        self.main_win.showStatusTips(
            "world pos: [{0},{1}]".format(pos.x(), pos.y()))

        if ev.button() == Qt.LeftButton:

            if self.cur_shape:
                self.cur_shape.addPoint(pos)
            else:
                self.cur_shape = Shape()
                self.cur_shape.fill = True
                self.cur_shape.addPoint(pos)
            self.repaint()

    def paintEvent(self, ev):
        # if not self.shapes:
        #     return super(Canvas, self).paintEvent(ev)
        if not self.image_wapper:
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
        return self.image_wapper.getQImage()

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

    def leaveEvent(self, ev):
        self.restoreCursor()

    def focusOutEvent(self, ev):
        self.restoreCursor()

    def enterEvent(self, ev):
        self.overrideCursor(self._curCursor)

    def overrideCursor(self, cursor):
        QApplication.restoreOverrideCursor()
        QApplication.setOverrideCursor(cursor)
        self._curCursor = cursor

    @staticmethod
    def restoreCursor():
        QApplication.restoreOverrideCursor()
