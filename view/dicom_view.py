from qtpy import QtWidgets, QtCore
from canvas import Canvas
from canvas import CREATE, EDIT
from imagedata_wapper import ImageDataWapper
import utils
from .base_view import BaseView
from .canvas_3d import Canvas3D


class DicomView(BaseView):

    canvas_list = []

    def __init__(self):
        super(DicomView, self).__init__()
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

        self.canvas_3d = Canvas3D()
        self.layout().addWidget(self.canvas_3d, 1, 1)

        for _, canvas in self.canvas_list:
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
        for i in range(3):
            _, canvas = self.canvas_list[i]
            wapper = ImageDataWapper(image_data, i)
            canvas.image_wapper = wapper

        self.canvas_3d.loadImage(image_data)

    def addMenu(self, actions):
        for i in range(3):
            _, canvas = self.canvas_list[i]
            utils.addActions(canvas.menu, actions)

    def toggleDrawMode(self, mode):
        for i in range(3):
            _, canvas = self.canvas_list[i]
            if mode:
                canvas.setMode(CREATE)
                canvas.setCreateMode(mode)
            else:
                canvas.setMode(EDIT)

    def editing(self):
        return self.canvas_list[0][1].editing()

    def __len__(self):
        return len(self.canvas_list)

    def __getitem__(self, i):
        return self.canvas_list[i][1]

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

        # self.scrollBars = {
        #     Qt.Horizontal: scrollArea.horizontalScrollBar(),
        #     Qt.Vertical: scrollArea.verticalScrollBar(),
        # }
