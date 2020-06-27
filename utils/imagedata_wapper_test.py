from PyQt5 import QtWidgets, QtGui, QtCore
from loader import Loader
from imagedata_wapper import ImageDataWapper
from vtk.util import numpy_support
import qimage2ndarray
import numpy as np
import vtk

import sys

loader = Loader()
loader.loadDicom(r"F:\github\labeldicom_cpp\testData\5_a.png")

wapper = ImageDataWapper(loader.getImageData())

img = loader.getImageData()
dim = img.GetDimensions()
channel = img.GetNumberOfScalarComponents()
nda = numpy_support.vtk_to_numpy(img.GetPointData().GetScalars())
nda = nda.reshape((dim[1], dim[0], 3), order='C')

app = QtWidgets.QApplication(sys.argv)
label = QtWidgets.QLabel()
qimg = qimage2ndarray.array2qimage(nda)
label.setPixmap(QtGui.QPixmap.fromImage(qimg))

label.show()

app.exec()
