from qtpy import QtWidgets, QtCore
import utils
from .canvas import Canvas
from .canvas import CREATE, EDIT
from utils import ImageDataWapper
from .base_view import BaseView
from .canvas_3d import Canvas3D
from type import Mode_box
from shape_box import ShapeBox


class DicomView(BaseView):
    def __init__(self):
        super(DicomView, self).__init__()
        self.scrollAreas = []
        m = (0, 0, 0, 0)
        self.setLayout(QtWidgets.QGridLayout())
        self.layout().setContentsMargins(*m)

        for i in range(3):
            canvas = Canvas()
            # canvas.resize(200, 200)
            scrollArea = QtWidgets.QScrollArea()
            scrollArea.setWidget(canvas)
            scrollArea.setWidgetResizable(True)
            scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            scrollArea.setHorizontalScrollBarPolicy(
                QtCore.Qt.ScrollBarAlwaysOff)
            self.scrollAreas.append(scrollArea)
            self.canvas_list.append(canvas)

        self.layout().addWidget(self.scrollAreas[0], 0, 0)
        self.layout().addWidget(self.scrollAreas[1], 0, 1)
        self.layout().addWidget(self.scrollAreas[2], 1, 0)

        self.canvas_3d = Canvas3D()
        self.layout().addWidget(self.canvas_3d, 1, 1)

        for i in range(self.layout().columnCount()):
            self.layout().setColumnStretch(i, 1)
            for j in range(self.layout().rowCount()):
                self.layout().setRowStretch(j, 1)

        self.initSlot()

    def _newShape(self, canvas, shapes):
        shapes_3d = []
        for shape in shapes:
            if shape.shape_type == Mode_box:
                shape.__class__ = ShapeBox
                shape.init(canvas)
                shapes_3d.append(shape)
                # shapes.remove(shape)
        for c in self.canvas_list:
            c.loadShapes(shapes_3d, False)
        self.newShape.emit(canvas, shapes)

    def curSliceIndexs(self):
        return [s.sliceIndex() for s in self.canvas_list]

    def loadImage(self, image_data):
        for i in range(3):
            canvas = self.canvas_list[i]
            wapper = ImageDataWapper(image_data, i)
            canvas.setImageWapper(wapper)

        for canvas in self.canvas_list:
            canvas.updateToCenter()

        self.canvas_3d.loadImage(image_data)

    def clear(self):
        self.canvas_3d.clear()
