from PyQt5 import QtGui
from PyQt5.QtCore import QObject, QPoint
from PyQt5.QtGui import QPen

DEFAULT_LINE_COLOR = QtGui.QColor(0, 255, 0, 128)
DEFAULT_FILL_COLOR = QtGui.QColor(255, 0, 0, 128)
DEFAULT_SELECT_LINE_COLOR = QtGui.QColor(255, 255, 255)
DEFAULT_SELECT_FILL_COLOR = QtGui.QColor(0, 128, 255, 155)
DEFAULT_VERTEX_FILL_COLOR = QtGui.QColor(0, 255, 0, 255)
DEFAULT_HVERTEX_FILL_COLOR = QtGui.QColor(255, 0, 0)


class Shape(QObject):
    P_SQUARE, P_ROUND = 0, 1

    line_color = DEFAULT_LINE_COLOR
    fill_color = DEFAULT_FILL_COLOR
    select_line_color = DEFAULT_SELECT_LINE_COLOR
    select_fill_color = DEFAULT_SELECT_FILL_COLOR
    vertex_fill_color = DEFAULT_VERTEX_FILL_COLOR
    hvertex_fill_color = DEFAULT_HVERTEX_FILL_COLOR

    point_size = 8
    point_type = P_ROUND
    scale = 1.0

    def __init__(self, label=None, line_color=None, shape_type=None):
        self.closed = False
        self.selected = False
        self.fill = False
        self.points = []

        self.label = label
        self.shape_type = shape_type
        if line_color is not None:
            self.line_color = line_color

    def paint(self, painter):
        if not self.points:
            return
        color = self.line_color
        if self.selected:
            color = self.select_line_color
        pen = QPen(color)
        pen.setWidth(max(1, round(2 / self.scale)))
        painter.setPen(pen)

        line_path = QtGui.QPainterPath()
        vrtx_path = QtGui.QPainterPath()

        line_path.moveTo(self.points[0])
        for i, p in enumerate(self.points):
            line_path.lineTo(p)
            self.drawVertex(vrtx_path, i)

        painter.drawPath(line_path)
        painter.drawPath(vrtx_path)
        painter.fillPath(vrtx_path, self.hvertex_fill_color)
        if self.fill:
            color = self.fill_color
            if self.selected:
                color = self.select_fill_color
            painter.fillPath(line_path, color)

    def drawVertex(self, path, i):
        r = self.point_size / self.scale * 0.5
        pos = self.points[i]

        if self.point_type == Shape.P_ROUND:
            path.addEllipse(pos, r, r)
        elif self.point_type == Shape.P_SQUARE:
            d = QPoint(r, r)
            path.addRect(pos + d, pos - d)

    def addPoint(self, point):
        if self.points and point == self.points[0]:
            self.closed = True
        else:
            self.points.append(point)

