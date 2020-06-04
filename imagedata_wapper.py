import vtk
from PyQt5.QtGui import QImage
from vtk.util import numpy_support as nps
import qimage2ndarray as q2nda

from loader import Loader


class ImageDataWapper:
    image_data = None
    qimage = None

    def __init__(self, image_data):
        self.image_data = image_data
        self.update()

    def update(self):
        dim = self.image_data.GetDimensions()
        nda = self.image_data.GetPointData().GetScalars()
        nda = nps.vtk_to_numpy(nda)
        nda = nda.reshape((dim[1], dim[0], 3), order='C')

        self.qimage = q2nda.array2qimage(nda)

    def getQImage(self):
        return self.qimage


if __name__ == "__main__":

    loader = Loader()
    loader.loadDicom(r"F:\github\labeldicom_cpp\testData\5_a.png")

    wapper = ImageDataWapper(loader.getImageData())
    wapper.getQImage()
