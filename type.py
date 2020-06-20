SHOW_IMG, SHOW_VIDEO, SHOW_MPR = 0, 1, 2

SLICE_X, SLICE_Y, SLICE_Z = 0, 1, 2

SUPPORT_FORMAT = ["BMP (*.bmp, *.BMP)",
                  "PNG ( *.png, *.PNG )",
                  "DICOM (*.dcm *.DCM *.dicom *.DICOM)",
                  "BioRad (*.PIC, *.pic)",
                  "Gipl (*.gipl *.gipl.gz)",
                  "JPEG ( *.jpg, *.JPG, *.jpeg, *.JPEG )",
                  "LSM ( *.tif, *.TIF, *.tiff, *.TIFF, *.lsm, *.LSM )",
                  "MINC ( *.mnc, *.MNC )",
                  "MRC ( *.mrc, *.rec )",
                  "Meta ( *.mha, *.mhd )",
                  "Nifti ( *.nia, *.nii, *.nii.gz, *.hdr, *.img, *.img.gz )",
                  "Nrrd ( *.nrrd, *.nhdr )",
                  "TIFF ( *.tif, *.TIF, *.tiff, *.TIFF )",
                  "VTK ( *.vtk )",
                  "JSON ( *.json )"
                  ]


Mode_polygon = 'polygon'
Mode_rectangle = 'rectangle'
Mode_circle = 'circle'
Mode_line = 'line'
Mode_point = 'point'
Mode_linestrip = 'linestrip'
Mode_tag = 'tag'
Mode_box = 'box'

Mode_ALL = (
    Mode_polygon,
    Mode_rectangle,
    Mode_circle,
    Mode_line,
    Mode_point,
    Mode_linestrip,
    Mode_tag,
    Mode_box,
)
