from qtpy import QtWidgets, QtCore, QtGui
from .canvas import Canvas, CREATE, EDIT
import utils


class BaseView(QtWidgets.QWidget):
    centerChanged = QtCore.Signal(Canvas, QtCore.QPointF)
    zoomChanged = QtCore.Signal(Canvas, float)
    frameChanged = QtCore.Signal(Canvas, int)
    drawingPolygon = QtCore.Signal(Canvas, bool)
    newShape = QtCore.Signal(Canvas, list)
    edgeSelected = QtCore.Signal(Canvas, bool)
    selectionChanged = QtCore.Signal(Canvas, list)
    onMousePress = QtCore.Signal(Canvas, QtCore.QPointF)

    def __init__(self):
        super(BaseView, self).__init__()
        self.canvas_list = []

    def initSlot(self):

        for canvas in self.canvas_list:
            canvas.zoomChanged.connect(
                lambda v, canvas=canvas: self.zoomChanged.emit(canvas, v))
            canvas.centerChanged.connect(
                lambda v, canvas=canvas: self.centerChanged.emit(canvas, v))
            canvas.frameChanged.connect(
                lambda v, canvas=canvas: self._frameChanged(canvas, v))
            canvas.selectionChanged.connect(
                lambda v, canvas=canvas: self.selectionChanged.emit(canvas, v))
            canvas.newShape.connect(
                lambda v, canvas=canvas: self._newShape(canvas, v))
            canvas.onMousePress.connect(
                lambda v, canvas=canvas: self.onMousePress.emit(canvas, v))

    def _frameChanged(self, canvas, shapes):
        self.frameChanged.emit(canvas, shapes)

    def _newShape(self, canvas, shapes):
        self.newShape.emit(canvas, shapes)

    def clear(self):
        pass

    def loadImage(self, image_data):
        pass

    def addMenu(self, actions):
        for _, canvas in enumerate(self.canvas_list):
            utils.addActions(canvas.menu, actions)

    def toggleDrawMode(self, mode):
        for _, canvas in enumerate(self.canvas_list):
            if mode:
                canvas.setMode(CREATE)
                canvas.setCreateMode(mode)
            else:
                canvas.setMode(EDIT)

    def selectShapes(self, shapes):
        if shapes:
            for c in self.canvas_list:
                c.selectShapes(shapes)
        else:
            for c in self.canvas_list:
                c.deSelectShape()

    def editing(self):
        if self.canvas_list:
            return self.canvas_list[0].editing()
        return False

    def __len__(self):
        return len(self.canvas_list)

    def __getitem__(self, i):
        return self.canvas_list[i]

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]


class ScrollArea(QtWidgets.QScrollArea):
    def __init__(self, *args, **kwargs):
        super(ScrollArea, self).__init__(*args, **kwargs)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def wheelEvent(self, ev):
        if ev.type() == QtCore.QEvent.Wheel:
            ev.ignore()
