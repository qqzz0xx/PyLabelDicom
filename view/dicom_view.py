from qtpy import QtWidgets, QtCore
import utils
from .canvas import Canvas
from .canvas import CREATE, EDIT
from utils import ImageDataWapper
from .base_view import BaseView, ScrollArea
from .canvas_3d import Canvas3D
from type import Mode_box
from shape_box import ShapeBox, Box3D


class DicomView(BaseView):
    def __init__(self):
        super(DicomView, self).__init__()
        self.scrollAreas = []
        self.shapes_3d = []
        m = (0, 0, 0, 0)
        self.setLayout(QtWidgets.QGridLayout())
        self.layout().setContentsMargins(*m)

        for i in range(3):
            canvas = Canvas()
            # canvas.resize(200, 200)
            scrollArea = ScrollArea()
            scrollArea.setWidget(canvas)
            # scrollArea.setWidgetResizable(True)
            # scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            # scrollArea.setHorizontalScrollBarPolicy(
            #     QtCore.Qt.ScrollBarAlwaysOff)
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
        slice_index = canvas.sliceIndex()
        slice_type = canvas.sliceType()
        new_shapes_3d = []
        win = QtWidgets.QApplication.instance().win
        label = win.getCurLabel()
        for shape in shapes:
            if shape.shape_type == Mode_box:
                shape.__class__ = ShapeBox
                box = Box3D(shape)
                shape.box = box
                box.label = label
                p1 = utils.sliceToVoxPos(canvas, shape[0])
                p1[slice_type] = slice_index + 20
                p2 = utils.sliceToVoxPos(canvas, shape[1])
                p2[slice_type] = slice_index - 20
                box.addPoint(p1)
                box.addPoint(p2)
                new_shapes_3d.append(box)

        self.newShape.emit(canvas, shapes)

        for canvas in self.canvas_list:
            rects = [
                s.getRectShape(canvas) for s in new_shapes_3d
                if isinstance(s, Box3D) and s.getRectShape(canvas)]
            canvas.loadShapes(rects, False)
        self.canvas_3d.refresh()

    def _frameChanged(self, canvas, v):
        self.frameChanged.emit(canvas, v)
        boxs = [s.box for s in utils.getMainWin().allLabelList.findShapesByType(Mode_box)]
        for canvas in self.canvas_list:
            rects = [box.getRectShape(canvas)
                     for box in boxs if box.getRectShape(canvas)]
            canvas.loadShapes(rects, False)

    def selectShapes(self, shapes):
        print(shapes)
        boxs = [s.box for s in shapes if s.shape_type == Mode_box]
        boxs_shapes = [s for box in boxs for s in box.shapes]
        shapes.extend(boxs_shapes)
        super(DicomView, self).selectShapes(shapes)

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
