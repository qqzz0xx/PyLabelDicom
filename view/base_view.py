from qtpy import QtWidgets, QtCore
from .canvas import Canvas


class BaseView(QtWidgets.QWidget):
    centerChanged = QtCore.Signal(Canvas, QtCore.QPointF)
    zoomChanged = QtCore.Signal(Canvas, float)
    nextFrame = QtCore.Signal(Canvas, QtCore.QPointF)
    drawingPolygon = QtCore.Signal(Canvas, bool)
    newShape = QtCore.Signal(Canvas, list)
    edgeSelected = QtCore.Signal(Canvas, bool)
    selectionChanged = QtCore.Signal(Canvas, list)
    onMousePress = QtCore.Signal(Canvas, QtCore.QPointF)
