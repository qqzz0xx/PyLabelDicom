from qtpy import QtWidgets, QtCore
import utils
from .canvas import Canvas
from .canvas import CREATE, EDIT
from utils import ImageDataWapper
from .base_view import BaseView
from .canvas_3d import Canvas3D


class DicomView(BaseView):

    def __init__(self):
        super(DicomView, self).__init__()

        self.scrollAreas = []
        m = (0, 0, 0, 0)
        self.setLayout(QtWidgets.QGridLayout())
        self.layout().setContentsMargins(*m)

        for i in range(3):
            canvas = Canvas(self)
            # canvas.resize(200, 200)
            scrollArea = QtWidgets.QScrollArea(self)
            scrollArea.setWidget(canvas)
            scrollArea.setWidgetResizable(True)
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

    def loadImage(self, image_data):
        for i in range(3):
            canvas = self.canvas_list[i]
            wapper = ImageDataWapper(image_data, i)
            canvas.image_wapper = wapper

        self.canvas_3d.loadImage(image_data)

        # self.scrollBars = {
        #     Qt.Horizontal: scrollArea.horizontalScrollBar(),
        #     Qt.Vertical: scrollArea.verticalScrollBar(),
        # }
