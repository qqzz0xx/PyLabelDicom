import vtk
from PyQt5.QtGui import QImage
from vtk.util import numpy_support as nps
import qimage2ndarray as q2nda

class ImageDataWapper:
    image_data : vtk.vtkImageData
    
    def __init__(self, image_data):
        self.image_data = image_data
    
    def getQImage(self):
        nda = nps.vtk_to_numpy(self.image_data)
        qimg = q2nda.array2qimage(nda)

        return qimg
        
        