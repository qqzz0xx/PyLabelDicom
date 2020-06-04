import vtk
from PyQt5.QtGui import QImage
from vtk.util import numpy_support as nps
import qimage2ndarray as q2nda

from loader import Loader


class ImageDataWapper:
    image_data: vtk.vtkImageData

    def __init__(self, image_data):
        self.image_data = image_data

    def getQImage(self):
        dim = self.image_data.GetDimensions()
        print(dim)
        channel = self.image_data.GetNumberOfScalarComponents()
        data = self.image_data.GetPointData().GetScalars()
        data = nps.vtk_to_numpy(data)

        qimg = QImage(data, dim[0], dim[1], QImage.Format_RGB32)

        return qimg


if __name__ == "__main__":

    loader = Loader()
    loader.loadDicom(r"E:\testData\5_a.png")

    wapper = ImageDataWapper(loader.getImageData())
    wapper.getQImage()
