import json
import os.path as osp
from shape import Shape


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

        saveDirName = dirname

    def loadLabels(self, path):
        with open(path) as f:
            j = json.load(f)

        shapes = []
        for d in j['shapes']:
            s = Shape(None, None)
            s.__dict__.update(d)
            shapes.append(s)

        return shapes
