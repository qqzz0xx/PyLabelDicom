import SimpleITK as sitk
from vtk.util import numpy_support as nps

import vtk


class Loader:
    image_data = vtk.vtkImageData()

    def getImageData(self):
        return self.image_data

    def loadDicom(self, path):
        if path is None:
            return
        self.image_path = path

        img_itk = sitk.ReadImage(path)
        spacing = img_itk.GetSpacing()
        dims = img_itk.GetSize()
        channel = img_itk.GetNumberOfComponentsPerPixel()
        frame_count = 1 if len(dims) == 2 else dims[2]
        spacing_z = 1 if len(dims) == 2 else spacing[2]

        img_nda = sitk.GetArrayFromImage(img_itk)
        img_nda = img_nda.astype('float32')

        importer = vtk.vtkImageImport()
        importer.SetDataScalarTypeToFloat()
        importer.SetNumberOfScalarComponents(channel)
        importer.SetDataExtent(0, dims[0]-1, 0, dims[1]-1, 0, frame_count-1)
        importer.SetWholeExtent(0, dims[0]-1, 0, dims[1]-1, 0, frame_count-1)
        importer.SetDataSpacing(spacing[0], spacing[1], spacing_z)
        importer.CopyImportVoidPointer(img_nda, img_nda.nbytes)
        importer.Update()

        output = importer.GetOutput()

        self.image_data.DeepCopy(output)

        print('load image info:')
        print(output)

        return self.image_data


if __name__ == "__main__":
    path = 'F:\\github\\labeldicom_cpp\\testData\\5_a.png'
    loader = Loader()
    img = loader.loadDicom(path)
    print(img)
