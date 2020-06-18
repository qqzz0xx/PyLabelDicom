from qtpy import QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk


class Canvas3D(QVTKRenderWindowInteractor):
    def __init__(self):
        super(Canvas3D, self).__init__()
        # self.setLayout(QtWidgets.QHBoxLayout())
        # self.vtkWidget = QVTKRenderWindowInteractor(self)
        colors = vtk.vtkNamedColors()
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(colors.GetColor3d("Tomato"))

        self.GetRenderWindow().AddRenderer(self.ren)
        # self.layout().addWidget(self.vtkWidget)

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
        self.render()

    def render(self):
        self.GetRenderWindow().Render()
