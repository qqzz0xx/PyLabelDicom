import SimpleITK as sitk
from vtk.util import numpy_support as nps
import numpy as np
import os.path as osp
import vtk
import skvideo.io as skio
import time


class Loader:
    image_data = vtk.vtkImageData()

    def getImageData(self):
        return self.image_data

    def isVolume(self):
        return self.image_type == 'volume'

    def isImage(self):
        return self.image_type == 'image'

    def isVideo(self):
        return self.image_type == 'video'

    def numpy_array_as_vtk_image_data(self, source_numpy_array):
        if len(source_numpy_array.shape) > 2:
            frame_count = source_numpy_array.shape[0]
        else:
            frame_count = 1

        channel_count = source_numpy_array.shape[-1]

        output_vtk_image = vtk.vtkImageData()
        output_vtk_image.SetDimensions(
            source_numpy_array.shape[2], source_numpy_array.shape[1], frame_count)

        vtk_type_by_numpy_type = {
            np.uint8: vtk.VTK_UNSIGNED_CHAR,
            np.uint16: vtk.VTK_UNSIGNED_SHORT,
            np.uint32: vtk.VTK_UNSIGNED_INT,
            np.uint64: vtk.VTK_UNSIGNED_LONG if vtk.VTK_SIZEOF_LONG == 64 else vtk.VTK_UNSIGNED_LONG_LONG,
            np.int8: vtk.VTK_CHAR,
            np.int16: vtk.VTK_SHORT,
            np.int32: vtk.VTK_INT,
            np.int64: vtk.VTK_LONG if vtk.VTK_SIZEOF_LONG == 64 else vtk.VTK_LONG_LONG,
            np.float32: vtk.VTK_FLOAT,
            np.float64: vtk.VTK_DOUBLE
        }
        vtk_datatype = vtk_type_by_numpy_type[source_numpy_array.dtype.type]

        # source_numpy_array = np.flipud(source_numpy_array)

        # Note: don't flip (take out next two lines) if input is RGB.
        # Likewise, BGRA->RGBA would require a different reordering here.
        # if channel_count > 1:
        #     source_numpy_array = np.flip(source_numpy_array, 2)

        depth_array = nps.numpy_to_vtk(
            source_numpy_array.ravel(), deep=True, array_type=vtk_datatype)
        depth_array.SetNumberOfComponents(channel_count)
        output_vtk_image.SetSpacing([1, 1, 1])
        output_vtk_image.SetOrigin([0, 0, 0])
        output_vtk_image.GetPointData().SetScalars(depth_array)

        output_vtk_image.Modified()
        return output_vtk_image

    def loadDicom(self, path):
        if path is None:
            return
        start_time = time.time()
        self.image_path = path
        self.image_dir = osp.dirname(osp.abspath(path))
        self.image_suffix = osp.splitext(path)[1]

        if str.lower(self.image_suffix) in ['.mp4', '.avi', '.flv', '.wmv']:
            img_nda = skio.vread(path)
            img_nda = img_nda.astype('float32')
            self.image_type = 'video'
            self._channel = img_nda.shape[3]
            self._spacing = (1, 1, 1)
            self._dims = (img_nda.shape[1], img_nda.shape[0], img_nda.shape[2])
            print(img_nda.shape)
            output = self.numpy_array_as_vtk_image_data(img_nda)
        else:
            img_itk = sitk.ReadImage(path)
            spacing = img_itk.GetSpacing()
            dims = img_itk.GetSize()
            channel = img_itk.GetNumberOfComponentsPerPixel()
            frame_count = 1 if len(dims) == 2 else dims[2]
            spacing_z = 1 if len(dims) == 2 else spacing[2]

            self._dims = (dims[0], dims[1], frame_count)
            self._spacing = (spacing[0], spacing[1], spacing_z)
            self._channel = channel
            self.image_type = 'image' if frame_count == 1 else 'volume'

            img_nda = sitk.GetArrayFromImage(img_itk)
            img_nda = img_nda.astype('float32')

            importer = vtk.vtkImageImport()
            importer.SetDataScalarTypeToFloat()
            importer.SetNumberOfScalarComponents(self._channel)
            importer.SetDataExtent(
                0, self._dims[0]-1, 0, self._dims[1]-1, 0, self._dims[2]-1)
            importer.SetWholeExtent(
                0, self._dims[0]-1, 0, self._dims[1]-1, 0, self._dims[2]-1)
            importer.SetDataSpacing(
                self._spacing[0], self._spacing[1], self._spacing[2])
            importer.CopyImportVoidPointer(img_nda, img_nda.nbytes)
            importer.Update()
            output = importer.GetOutput()

        print(output)
        self.image_data.DeepCopy(output)

        print("---laod dicom:  %s seconds ---" % (time.time() - start_time))
        # print('load image info:')
        # print(output)

        return self.image_data


if __name__ == "__main__":
    path = 'F:\\github\\labeldicom_cpp\\testData\\06705_02_1024X768.mp4'
    loader = Loader()
    img = loader.loadDicom(path)
    print(img)
