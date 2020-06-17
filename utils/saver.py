import json
import os.path as osp


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
            slice_index=s.slice_index

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
