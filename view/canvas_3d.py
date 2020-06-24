from qtpy import QtWidgets, QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk
from type import Mode_point
import utils


class SphereActor(vtk.vtkActor):
    def __init__(self):
        colors = vtk.vtkNamedColors()
        # Create a sphere
        sphereSource = vtk.vtkSphereSource()
        sphereSource.SetCenter(0.0, 0.0, 0.0)
        sphereSource.SetRadius(5.0)
        # Make the surface smooth.
        sphereSource.SetPhiResolution(100)
        sphereSource.SetThetaResolution(100)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphereSource.GetOutputPort())

        self.SetMapper(mapper)
        self.GetProperty().SetColor(colors.GetColor3d("Cornsilk"))


class Canvas3D(QtWidgets.QFrame):
    def __init__(self):
        super(Canvas3D, self).__init__()
        self.shapes = []

        m = (0, 0, 0, 0)
        self.vl = QtWidgets.QVBoxLayout()
        self.vl.setContentsMargins(*m)
        self.iren = QVTKRenderWindowInteractor(self)
        self.vl.addWidget(self.iren)
        self.setLayout(self.vl)

        colors = vtk.vtkNamedColors()
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(colors.GetColor3d("SkyBlue"))
        self.renWin().AddRenderer(self.ren)

    def __del__(self):
        # self.iren.Finalize()
        print('~Canvas3D', self)

    def loadImage(self, image_data):
        r = image_data.GetScalarRange()
        n = image_data.GetNumberOfScalarComponents()
        print(r)
        print(n)
        # Create transfer mapping scalar value to opacity.
        opacityTransferFunction = vtk.vtkPiecewiseFunction()
        opacityTransferFunction.AddPoint(0, 0.0)
        opacityTransferFunction.AddPoint(255, 1.0)

        # Create transfer mapping scalar value to color.
        colorTransferFunction = vtk.vtkColorTransferFunction()
        colorTransferFunction.AddRGBPoint(0.0, 0.0, 0.0, 0.0)
        colorTransferFunction.AddRGBPoint(10.0, 0.1, 0.1, 0.1)
        colorTransferFunction.AddRGBPoint(255.0, 1.0, 1.0, 1.0)

        # The property describes how the data will look.
        volumeProperty = vtk.vtkVolumeProperty()
        volumeProperty.SetColor(colorTransferFunction)
        volumeProperty.SetScalarOpacity(opacityTransferFunction)
        volumeProperty.ShadeOn()
        volumeProperty.SetInterpolationTypeToLinear()

        # The mapper / ray cast function know how to render the data.
        volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
        volumeMapper.SetInputData(image_data)
        volumeMapper.SetBlendModeToComposite()
        volumeMapper.Update()
        # The volume holds the mapper and the property and
        # can be used to position/orient the volume.
        volume = vtk.vtkVolume()
        volume.SetMapper(volumeMapper)
        volume.SetProperty(volumeProperty)

        self.ren.AddVolume(volume)
        self.ren.ResetCameraClippingRange()
        self.ren.ResetCamera()
        self.renWin().Render()

    def renWin(self):
        return self.iren.GetRenderWindow()

    def clear(self):
        self.ren.RemoveAllViewProps()
        self.iren.Finalize()

    def getShapes(self):
        win = utils.getMainWin()
        shapes = [item.shape() for item in win.allLabelList if item.shape().shape_type ==
                  Mode_point]

        return shapes

    def refresh(self):
        print('refresh')
        shapes = self.getShapes()
        shapes = [s for s in shapes if s not in self.shapes]
        for s in self.getShapes():
            canvas = utils.getMainWin().view[s.slice_type]
            mat = canvas.image_wapper.getImageToVoxMatrix()
            vpos = utils.sliceToVoxPos1(s.slice_type, s.slice_index, mat, s[0])

            actor = SphereActor()
            actor.SetPosition(*vpos)
            self.ren.AddActor(actor)
            self.shapes.append(s)
            print('add {} to 3d'.format(s))
