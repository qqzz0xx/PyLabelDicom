from qtpy import QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk


class Canvas3D(QtWidgets.QWidget):
    def __init__(self):
        super(Canvas3D, self).__init__()
        self.setLayout(QtWidgets.QHBoxLayout())
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.layout().addWidget(self.vtkWidget)

    def test_load(self):
        colors = vtk.vtkNamedColors()
        # Set the background color.
        bkg = map(lambda x: x / 255.0, [26, 51, 102, 255])
        colors.SetColor("BkgColor", *bkg)

        # This creates a polygonal cylinder model with eight circumferential
        # facets.
        cylinder = vtk.vtkCylinderSource()
        cylinder.SetResolution(8)

        # The mapper is responsible for pushing the geometry into the graphics
        # library. It may also do color mapping, if scalars or other
        # attributes are defined.
        cylinderMapper = vtk.vtkPolyDataMapper()
        cylinderMapper.SetInputConnection(cylinder.GetOutputPort())

        # The actor is a grouping mechanism: besides the geometry (mapper), it
        # also has a property, transformation matrix, and/or texture map.
        # Here we set its color and rotate it -22.5 degrees.
        cylinderActor = vtk.vtkActor()
        cylinderActor.SetMapper(cylinderMapper)
        cylinderActor.GetProperty().SetColor(colors.GetColor3d("Tomato"))
        cylinderActor.RotateX(30.0)
        cylinderActor.RotateY(-45.0)

        # Add the actors to the renderer, set the background and size
        self.ren.AddActor(cylinderActor)
        self.ren.SetBackground(colors.GetColor3d("BkgColor"))
        self.ren.ResetCameraClippingRange()
        self.render()

    def loadImage(self, image_data):
                # Create transfer mapping scalar value to opacity.
        opacityTransferFunction = vtk.vtkPiecewiseFunction()
        opacityTransferFunction.AddPoint(0, 0.0)
        opacityTransferFunction.AddPoint(255, 1.0)

        # Create transfer mapping scalar value to color.
        colorTransferFunction = vtk.vtkColorTransferFunction()
        colorTransferFunction.AddRGBPoint(0.0, 0.0, 0.0, 1.0)
        colorTransferFunction.AddRGBPoint(40.0, 1.0, 0.0, 0.0)
        colorTransferFunction.AddRGBPoint(255.0, 1.0, 1.0, 1.0)

        # The property describes how the data will look.
        volumeProperty = vtk.vtkVolumeProperty()
        volumeProperty.SetColor(colorTransferFunction)
        volumeProperty.SetScalarOpacity(opacityTransferFunction)
        volumeProperty.ShadeOn()
        # volumeProperty.SetInterpolationTypeToLinear()

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
        self.vtkWidget.GetRenderWindow().Render()
