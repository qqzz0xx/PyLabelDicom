from shape_box import Box3D, ShapeBox
from qtpy import QtCore
import json
import os.path as osp
from shape import Shape
from type import Mode_box
import utils


class Saver:
    saveDirName = None
    suffix = ".json"

    def formatShape(self, s):
        data = dict(
            label=s.label.__dict__,
            points=[(p.x(), p.y()) for p in s.points],
            shape_type=s.shape_type,
            flags=s.flags,
            slice_type=s.slice_type,
            slice_index=s.slice_index,
            _closed=s._closed,
        )
        if s.shape_type == Mode_box:
            data['box'] = s.box.bounds

        return data

    def saveLabels(self, dirname, shapes, imagePath):
        data = dict(
            imagePath=imagePath,
            shapes=[self.formatShape(s) for s in shapes]
        )

        filename = osp.basename(imagePath).split('.')[0] + self.suffix
        path = osp.join(dirname, filename)

        print("save: ", path)

        with open(path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.saveDirName = dirname

    def loadLabels(self, j):
        shapes = []
        for d in j['shapes']:
            s = Shape(None, None)
            s.__dict__.update(d)
            s.label = utils.struct(**s.label)
            s.points = [QtCore.QPointF(x, y) for x, y in s.points]
            if s.shape_type == Mode_box:
                box = Box3D(s)
                box.bounds = d['box']
                box.label = s.label
                s.box = box
                s.__class__ = ShapeBox
            shapes.append(s)

        return shapes
