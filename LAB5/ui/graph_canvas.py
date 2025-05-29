import numpy as np
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QPolygonF
from PySide6.QtCore import Qt, QPointF

class GraphCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.graph = None
        self.best = None
        self.second = None
        self.worst = None
        self.radius = 12
        self.margin = 40

    def set_graph_and_paths(self, graph, best, second, worst):
        self.graph = graph
        self.best = best
        self.second = second
        self.worst = worst
        self.update()

    def paintEvent(self, event):
        if self.graph is None:
            return
        n = self.graph.shape[0]
        w = self.width() - 2*self.margin
        h = self.height() - 2*self.margin
        center_x = self.width() // 2
        center_y = self.height() // 2
        r = min(w, h) // 2
        coords = [
            (center_x + r * np.cos(2*np.pi*i/n), center_y + r * np.sin(2*np.pi*i/n))
            for i in range(n)
        ]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        pen = QPen(QColor(180,180,180), 1)
        painter.setPen(pen)
        for i in range(n):
            for j in range(i+1, n):
                painter.drawLine(int(coords[i][0]), int(coords[i][1]), int(coords[j][0]), int(coords[j][1]))
        
        def draw_path(path, color, width):
            pen = QPen(color, width)
            painter.setPen(pen)
            for i in range(n):
                a = path[i]
                b = path[(i+1)%n]
                x1, y1 = coords[a]
                x2, y2 = coords[b]
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
                self.draw_arrow(painter, x1, y1, x2, y2, color)
        if self.worst:
            draw_path(self.worst, QColor(220,40,40), 3)
        if self.second:
            draw_path(self.second, QColor(40,180,40), 3)
        if self.best:
            draw_path(self.best, QColor(40,40,220), 4)
        
        for i, (x, y) in enumerate(coords):
            if self.best:
                if i == self.best[0]:
                    painter.setPen(QPen(QColor(255,140,0), 3))  
                    painter.setBrush(QColor(255,255,200))
                elif i == self.best[-1]:
                    painter.setPen(QPen(QColor(0,180,180), 3))  
                    painter.setBrush(QColor(220,255,255))
                else:
                    painter.setPen(QPen(Qt.black, 1))
                    painter.setBrush(QColor(255,255,255))
            else:
                painter.setPen(QPen(Qt.black, 1))
                painter.setBrush(QColor(255,255,255))
            painter.drawEllipse(int(x)-self.radius, int(y)-self.radius, 2*self.radius, 2*self.radius)
            painter.drawText(int(x)-6, int(y)+6, str(i))
        painter.end()

    def draw_arrow(self, painter, x1, y1, x2, y2, color):
        
        vec = np.array([x2-x1, y2-y1])
        length = np.linalg.norm(vec)
        if length < 1e-2:
            return
        vec = vec / length
        
        arrow_len = 18
        arrow_width = 7
        px = x2 - vec[0]*self.radius
        py = y2 - vec[1]*self.radius
        left = np.array([-vec[1], vec[0]])
        p1 = QPointF(px, py)
        p2 = QPointF(px - vec[0]*arrow_len + left[0]*arrow_width, py - vec[1]*arrow_len + left[1]*arrow_width)
        p3 = QPointF(px - vec[0]*arrow_len - left[0]*arrow_width, py - vec[1]*arrow_len - left[1]*arrow_width)
        painter.setBrush(color)
        painter.setPen(QPen(color, 1))
        painter.drawPolygon(QPolygonF([p1, p2, p3])) 