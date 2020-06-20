from shape import Shape
from qtpy import QtGui
from type import Mode_box


class ShapeBox(Shape):
    height = 50

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
