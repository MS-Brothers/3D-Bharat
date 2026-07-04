# measurement_widget.py

from PyQt5.QtWidgets import (QWidget)
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPen, QFont, QColor

from math import sqrt

# Create a class for Measurements::
class MeasurementWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.points = []
        self.lines = []
        self.measurement_type = None
        self.measurement_data = {}
        self.font = QFont()
        self.font.setPointSize(10)
        
    # Define a function for the set measurement:
    def set_measurement_type(self, m_type):
        self.measurement_type = m_type
        self.points = []
        self.lines = []
        
        # Set predefined points based on measurement type
        if m_type == 'line':
            self.points = [
                QPoint(50, 100),  # Point A
                QPoint(150, 100)  # Point B
            ]
        elif m_type == 'polygon':
            self.points = []  # Start with empty points for polygon
            
        self.update()
    
    # Function for add point:
    def add_point(self, point):
        if self.measurement_type in ['line','polygon']:
            self.points.append(point)
        self.update()
    
    # Function for add Line:
    def add_line(self, line):
        self.lines.append(line)
        self.update()
    
    # Function for clear points and lines:
    def clear(self):
        self.points = []
        self.lines = []
        self.measurement_type = None
        self.measurement_data = {}
        self.update()

    # def paintEvent(self, event):
    #     painter = QPainter(self)
    #     painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw points
        # for i, point in enumerate(self.points):
        #     color = QColor(100, 100, 100)  # Grey color for points
        #     painter.setPen(QPen(color, 8))
        #     painter.drawPoint(point)
            
        #     # Label points
        #     label = chr(65 + i)  # A, B, C, ...
        #     painter.setPen(QPen(Qt.black, 1))
        #     painter.setFont(self.font)
        #     painter.drawText(point.x() + 10, point.y() + 5, label)
        
        # # Draw lines (green color)
        # pen = QPen(QColor(0, 200, 0), 2)  # Green
        # painter.setPen(pen)
        
        # for line in self.lines:
        #     painter.drawLine(line[0], line[1])
        
        # # Draw angle labels if we have a triangle, rectangle or polygon
        # if self.measurement_type == 'polygon':
        #     self.draw_angle_labels(painter)

    # Define function for Draw angle labels in "Action" Section:
    def draw_angle_labels(self, painter):
        angle_pen = QPen(QColor(0, 0, 255), 1)
        painter.setPen(angle_pen)
        painter.setFont(self.font)
        
        if self.measurement_type == 'polygon' and len(self.points) >= 3:
            angles = self.measurement_data.get('angles', {})
            
            # Draw angle labels at each corner
            n = len(self.points)
            for i in range(n):
                a = self.points[i]
                b = self.points[(i+1)%n]
                c = self.points[(i+2)%n]
                label = chr(65 + (i+1)%n)
                angle = angles.get(label, 0)
                self.draw_angle_label(painter, a, b, c, f"{label} = {angle:.1f}°", 20)

    # Define the function for the draw angle label on point cloud data:
    def draw_angle_label(self, painter, vertex, p1, p2, text, offset):
        # Calculate angle bisector direction
        dir1_x = vertex.x() - p1.x()
        dir1_y = vertex.y() - p1.y()
        dir2_x = vertex.x() - p2.x()
        dir2_y = vertex.y() - p2.y()
        
        # Calculate bisector as float first
        bisector_x = (dir1_x + dir2_x) / 2
        bisector_y = (dir1_y + dir2_y) / 2
        
        # Normalize and scale
        length = sqrt(bisector_x**2 + bisector_y**2)
        if length > 0:
            bisector_x = bisector_x / length * offset
            bisector_y = bisector_y / length * offset
        
        # Create QPoint with rounded coordinates
        bisector = QPoint(int(round(bisector_x)), int(round(bisector_y)))
        
        # Position the label with rounded coordinates
        label_pos = QPoint(
            vertex.x() + bisector.x(),
            vertex.y() + bisector.y()
        )
        painter.drawText(label_pos, text)
    
    # Define the fucntion for depth:
    def set_depth_values(self, depths):
        """Store depth values for each point"""
        self.depth_values = depths
        self.update()
