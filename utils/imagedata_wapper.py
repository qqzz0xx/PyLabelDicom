import vtk
from PyQt5.QtGui import QImage
from vtk.util import numpy_support as nps
import qimage2ndarray as q2nda

import type
from utils import Loader


class ImageDataWapper:
    image_data = None
    qimage = None
    sliceType = None
    sliceIndex = 0
    maxFrame = 0

    def __init__(self, image_data, slice_type=type.SLICE_Z):
        self.image_data = image_data
        self.sliceType = slice_type

        self._spacing = self.image_data.GetSpacing()
        self._extent = self.image_data.GetExtent()
        self._dims = self.image_data.GetDimensions()
        self.maxFrame = self._dims[2] - 1
        self._channel = self.image_data.GetNumberOfScalarComponents()

        self._center = [0, 0, 0]
        self._center[0] = int(self._spacing[0] * 0.5 *
                              (self._extent[0] + self._extent[1]))
        self._center[1] = int(self._spacing[1] * 0.5 *
                              (self._extent[2] + self._extent[3]))
        self._center[2] = int(self._spacing[2] * 0.5 *
                              (self._extent[4] + self._extent[5]))

        self._reslice = vtk.vtkImageReslice()
        self._reslice.SetOutputDimensionality(2)
        self._resliceMatrix = self.getInitMatrix()

    def getResliceMatrix(self):
        matrix = vtk.vtkMatrix4x4()
        matrix.DeepCopy(self._resliceMatrix)
        return matrix

    def getCenterFrameIndex(self):
        if not self.image_data:
            return
        return self._center[self.sliceType]

    def getInitMatrix(self):
        slice_type = self.sliceType

        matrix = vtk.vtkMatrix4x4()
        matrix.Zero()
        matrix.SetElement(0, 3, self._center[0])
        matrix.SetElement(1, 3, self._center[1])
        matrix.SetElement(2, 3, self._center[2])
        matrix.SetElement(3, 3, 1)

        if slice_type is type.SLICE_X:
            matrix.SetElement(1, 0, 1)
            matrix.SetElement(0, 2, 1)
            matrix.SetElement(2, 1, 1)
        elif slice_type is type.SLICE_Y:
            matrix.SetElement(0, 0, 1)
            matrix.SetElement(1, 2, 1)
            matrix.SetElement(2, 1, 1)
        elif slice_type is type.SLICE_Z:
            matrix.SetElement(0, 0, 1)
            matrix.SetElement(1, 1, 1)
            matrix.SetElement(2, 2, 1)

        return matrix

    def conv2qimg(self, data):
        dim = data.GetDimensions()
        nda = data.GetPointData().GetScalars()
        nda = nps.vtk_to_numpy(nda)
        nda = nda.reshape((dim[1], dim[0], 3), order='C')
        self.qimage = q2nda.array2qimage(nda)
        return self.qimage

    def update(self, idx):
        if not self.image_data:
            return
        if idx < 0 or idx > self.maxFrame:
            return

        out_data = self.image_data
        if self._dims[2] <= 1 and self.sliceType == type.SLICE_Z:
            pass
        else:
            x, y, z = self._center
            st = self.sliceType
            if st is type.SLICE_X:
                x = idx * self._spacing[0]
            elif st is type.SLICE_Y:
                y = idx * self._spacing[1]
            elif st is type.SLICE_Z:
                z = idx * self._spacing[2]

            self._resliceMatrix.SetElement(0, 3, x)
            self._resliceMatrix.SetElement(1, 3, y)
            self._resliceMatrix.SetElement(2, 3, z)
            self._reslice.SetResliceAxes(self._resliceMatrix)
            self._reslice.SetInputData(out_data)
            self._reslice.Update()
            out_data = self._reslice.GetOutput()
            self.sliceIndex = idx

        if out_data.GetNumberOfScalarComponents() == 1:
            imageToRgb = vtk.vtkImageMapToColors()
            imageToRgb.SetOutputFormatToRGB()
            imageToRgb.SetLookupTable(vtk.vtkScalarsToColors())
            imageToRgb.SetInputData(out_data)
            imageToRgb.Update()
            out_data = imageToRgb.GetOutput()

        if out_data.GetScalarType() != vtk.VTK_UNSIGNED_CHAR:
            shift = vtk.vtkImageShiftScale()
            shift.SetOutputScalarTypeToUnsignedChar()
            shift.SetInputData(out_data)
            shift.Update()
            out_data = shift.GetOutput()

        out_data = self.conv2qimg(out_data)

        return out_data

    def getQImage(self):
        return self.qimage


if __name__ == "__main__":

    loader = Loader()
    d = loader.loadDicom(r"F:\github\labeldicom_cpp\testData\5_a.png")

    wapper = ImageDataWapper(d)
    wapper.getQImage()
