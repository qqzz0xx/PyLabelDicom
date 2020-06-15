from qtpy import QtWidgets, QtCore
from qtpy.QtWidgets import QSizePolicy, QPushButton
from canvas import Canvas


class DicomView(QtWidgets.QWidget):
    centerChanged = QtCore.Signal(Canvas, QtCore.QPointF)
    zoomChanged = QtCore.Signal(Canvas, float)
    nextFrame = QtCore.Signal(Canvas, QtCore.QPointF)
    drawingPolygon = QtCore.Signal(Canvas, bool)
    newShape = QtCore.Signal(Canvas, list)
    edgeSelected = QtCore.Signal(Canvas, bool)
    selectionChanged = QtCore.Signal(Canvas, list)

    canvas_list = []

    def __init__(self):
        super(DicomView, self).__init__()
        self.setSizePolicy(QSizePolicy.Policy.Preferred,
                           QSizePolicy.Policy.Preferred)
        self.setLayout(QtWidgets.QGridLayout())

        for i in range(3):
            canvas = Canvas(self)
            canvas.resize(200, 200)
            scrollArea = QtWidgets.QScrollArea(self)
            scrollArea.setWidget(canvas)
            scrollArea.setWidgetResizable(True)
            self.canvas_list.append((scrollArea, canvas))

        self.layout().addWidget(self.canvas_list[0][0], 0, 0)
        self.layout().addWidget(self.canvas_list[1][0], 0, 1)
        self.layout().addWidget(self.canvas_list[2][0], 1, 0)

        for _, canvas in self.canvas_list:
            canvas.zoomChanged.connect(
                lambda v: self.zoomChanged.emit(canvas, v))
            canvas.centerChanged.connect(
                lambda v: self.centerChanged.emit(canvas, v))
            canvas.nextFrame.connect(
                lambda v: self.nextFrame.emit(canvas, v))
            canvas.selectionChanged.connect(
                lambda v: self.selectionChanged.emit(canvas, v))
            canvas.newShape.connect(lambda v: self.newShape.emit(canvas, v))

    def loadImage(self, image_data):
        for i in range(3):
            wapper = ImageDataWapper(image_data, i)
            _, canvas = self.canvas_list[i]
            canvas.image_wapper = wapper

        # self.scrollBars = {
        #     Qt.Horizontal: scrollArea.horizontalScrollBar(),
        #     Qt.Vertical: scrollArea.verticalScrollBar(),
        # }
