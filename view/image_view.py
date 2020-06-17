from .base_view import BaseView
from .canvas import Canvas


class ImageView(BaseView):
    def __init__(self):
        super(ImageView, self).__init__()

        canvas = Canvas(self)
        scrollArea = QtWidgets.QScrollArea(self)
        scrollArea.setWidget(canvas)
        scrollArea.setWidgetResizable(True)
        self.scrollArea = scrollArea
        self.canvas_list.append(canvas)

        self.initSlot()

    def loadImage(self, image_data):

        canvas = self[0]
        wapper = ImageDataWapper(image_data, 2)
        canvas.image_wapper = wapper
