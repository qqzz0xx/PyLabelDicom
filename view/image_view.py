from qtpy import QtWidgets, QtCore
from qtpy.QtWidgets import QSizePolicy
from .base_view import BaseView
from .canvas import Canvas
from utils import ImageDataWapper


class ImageView(BaseView):
    def __init__(self):
        super(ImageView, self).__init__()
        m = (0, 0, 0, 0)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setContentsMargins(*m)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        canvas = Canvas()
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidget(canvas)
        scrollArea.setWidgetResizable(True)
        scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.layout().addWidget(scrollArea)

        self.canvas_list.append(canvas)

        self.initSlot()

    def loadImage(self, image_data):
        canvas = self[0]
        wapper = ImageDataWapper(image_data, 2)
        canvas.setImageWapper(wapper)
