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

    def __init__(self, *args, **kwargs):
        super(Canvas, self).__init__()
        self._curCursor = CURSOR_DEFAULT
        self.shapes = []
        self.cur_shape = None
        self._Painter = QtGui.QPainter()

        self.setMouseTracking(True)

    def mouseMoveEvent(self, ev):
        self.overrideCursor(CURSOR_DRAW)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            pos = ev.localPos()

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

        p = self._Painter
        p.begin(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.HighQualityAntialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        p.setPen(QColor(255, 0, 0))

        for shape in self.shapes:
            shape.paint(p)

        if self.cur_shape:
            self.cur_shape.paint(p)
            
        p.end()

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
