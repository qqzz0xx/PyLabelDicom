from qtpy import QtWidgets, QtCore
from .canvas import Canvas, CREATE, EDIT
import utils


class BaseView(QtWidgets.QWidget):
    centerChanged = QtCore.Signal(Canvas, QtCore.QPointF)
    zoomChanged = QtCore.Signal(Canvas, float)
    nextFrame = QtCore.Signal(Canvas, QtCore.QPointF)
    drawingPolygon = QtCore.Signal(Canvas, bool)
    newShape = QtCore.Signal(Canvas, list)
    edgeSelected = QtCore.Signal(Canvas, bool)
    selectionChanged = QtCore.Signal(Canvas, list)
    onMousePress = QtCore.Signal(Canvas, QtCore.QPointF)

    def __init__(self):
        super(BaseView, self).__init__()
        self.canvas_list = []
        print("BaseView:", self)
        print("canvas_list:", self.canvas_list)

    def initSlot(self):

        for canvas in self.canvas_list:
            canvas.zoomChanged.connect(
                lambda v, canvas=canvas: self.zoomChanged.emit(canvas, v))
            canvas.centerChanged.connect(
                lambda v, canvas=canvas: self.centerChanged.emit(canvas, v))
            canvas.nextFrame.connect(
                lambda v, canvas=canvas: self.nextFrame.emit(canvas, v))
            canvas.selectionChanged.connect(
                lambda v, canvas=canvas: self.selectionChanged.emit(canvas, v))
            canvas.newShape.connect(
                lambda v, canvas=canvas: self.newShape.emit(canvas, v))
            canvas.onMousePress.connect(
                lambda v, canvas=canvas: self.onMousePress.emit(canvas, v))

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
