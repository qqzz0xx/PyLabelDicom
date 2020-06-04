import SimpleITK as sitk
from vtk.util import numpy_support as nps

import vtk


class Loader:
    image_data = None

    def getImageData(self):
        return self.image_data

    def loadDicom(self, path):
        if path is None:
            return
            
        img_itk = sitk.ReadImage(path)
        spacing = img_itk.GetSpacing()
        dims = img_itk.GetSize()
        channel = img_itk.GetDimension()
        frame_count = 1 if len(dims) == 2 else dims[2]

        img_nda = sitk.GetArrayFromImage(img_itk)
        img_nda = img_nda.astype('float32')

        importer = vtk.vtkImageImport()
        importer.SetDataScalarTypeToFloat()
        importer.SetNumberOfScalarComponents(channel)
        importer.SetDataExtent(0, dims[2]-1, 0, dims[1]-1, 0, dims[0]-1)
        importer.SetWholeExtent(0, dims[2]-1, 0, dims[1]-1, 0, dims[0]-1)
        importer.SetDataSpacing(spacing[0], spacing[1], spacing[2])
        importer.CopyImportVoidPointer(img_nda, img_nda.nbytes)
        importer.Update()

        self.image_data = importer.GetOutput()

        return self.image_data


if __name__ == "__main__":
    path = 'F:\\github\\labeldicom_cpp\\testData\\AT0000_002585271512.dcm'
    loader = Loader()
    img = loader.loadDicom(path)
    print(img)
