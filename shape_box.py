from shape import Shape
from qtpy import QtGui
from type import Mode_box
import utils
import numpy as np


class ShapeBox(Shape):
    height = 50
    bounds = []

    def init(self, canvas):
        p1 = utils.sliceToVoxPos(canvas, self[0])
        p2 = utils.sliceToVoxPos(canvas, self[1])
        offset = [0, 0, 0]
        offset[canvas.sliceType()] = int(self.height / 2)
        p1 = np.array(p1[0:3])
        p2 = np.array(p2[0:3])
        p1 += offset
        p2 -= offset

        xmin = min(p1[0], p2[0])
        ymin = min(p1[1], p2[1])
        zmin = min(p1[2], p2[2])

        xmax = max(p1[0], p2[0])
        ymax = max(p1[1], p2[1])
        zmax = max(p1[2], p2[2])

        bds = [xmin, xmax, ymin, ymax, zmin, zmax]

        print(bds)
        print(p1)
        print(p2)

    def nearestVertex(self, point, epsilon, canvas):
        min_distance = float('inf')
        min_i = None
        for i, p in enumerate(self.points):
            dist = utils.distance(p - point)
            if dist <= epsilon and dist < min_distance:
                min_distance = dist
                min_i = i
        return min_i

    def nearestEdge(self, point, epsilon, canvas):
        min_distance = float('inf')
        post_i = None
        for i in range(len(self.points)):
            line = [self.points[i - 1], self.points[i]]
            dist = utils.distancetoline(point, line)
            if dist <= epsilon and dist < min_distance:
                min_distance = dist
                post_i = i
        return post_i

    def paint(self, canvas, painter):
        if not self.points:
            return
        if len(self.points) != 2:
            return

        color = self.select_line_color \
            if self.selected else self.line_color
        pen = QtGui.QPen(color)
        # Try using integer sizes for smoother drawing(?)
        pen.setWidth(max(1, int(round(2.0 / self.scale))))
        painter.setPen(pen)

        line_path = QtGui.QPainterPath()
        vrtx_path = QtGui.QPainterPath()

        curIdx = canvas.sliceIndex()
        curTy = canvas.sliceType()
        halfH = int(self.height / 2)
        h = curIdx - self.slice_index

        if curTy == self.slice_type:
            if h <= halfH and h > -halfH:
                rectangle = self.getRectFromLine(*self.points)
                line_path.addRect(rectangle)
                for i in range(len(self.points)):
                    self.drawVertex(vrtx_path, i)

        painter.drawPath(line_path)
        painter.drawPath(vrtx_path)
        painter.fillPath(vrtx_path, self._vertex_fill_color)
        if self.fill:
            color = self.select_fill_color \
                if self.selected else self.fill_color
            painter.fillPath(line_path, color)
