"""
Tool Development Kit for SideFX Houdini
Copyright (C) 2021  Ivan Titov

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import print_function

import json
import os

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

    Signal = pyqtSignal
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

import hou


class BoundingRectF(QRectF):
    def __init__(self, *args):
        super(BoundingRectF, self).__init__(*args)

        self.__initial = True

    def normalize(self):
        if self.width() < 0:
            left = self.left()
            self.setLeft(self.right())
            self.setRight(left)

        if self.height() < 0:
            top = self.top()
            self.setTop(self.bottom())
            self.setBottom(top)

    def addPosition(self, x, y):
        if self.__initial:
            self.moveTo(x, y)
            self.__initial = False
            return

        if x < self.left():
            self.setLeft(x)
        elif x > self.right():
            self.setRight(x)

        if y < self.top():
            self.setTop(y)
        elif y > self.bottom():
            self.setBottom(y)

    def addPoint(self, point):
        self.addPosition(point.x(), point.y())

    def addPositions(self, positions):
        if not positions:
            return

        if self.__initial:
            left = top = float('+inf')
            right = bottom = float('-inf')
            self.__initial = False
        else:
            left = self.left()
            top = self.top()
            right = self.right()
            bottom = self.bottom()

        for x, y in positions:
            left = min(x, left)
            top = min(y, top)
            right = max(x, right)
            bottom = max(y, bottom)

        self.setCoords(left, top, right, bottom)

    @staticmethod
    def fromPositions(positions):
        new = BoundingRectF()
        new.addPositions(positions)
        return new

    def addPoints(self, points):
        self.addPositions((point.x(), point.y()) for point in points)

    @staticmethod
    def fromPoints(points):
        new = BoundingRectF()
        new.addPoints(points)
        return new


EXCLUDED_SHAPES = ('vop', 'task', 'shop', 'cop2', 'subnet_input')


class NodeShape(object):

    def __init__(self):
        self.__valid = False
        self.__name = None
        self.__points = ()

    def isValid(self):
        return self.__valid

    def __bool__(self):
        return self.__valid

    def name(self):
        return self.__name

    def __copy__(self):
        new = NodeShape()
        new.__name = self.__name
        new.__points = self.__points
        new.__valid = self.__valid
        return new

    def copy(self):
        return self.__copy__()

    def transformToRect(self, rect, aspect_ratio_mode=Qt.KeepAspectRatio):
        target_rect = QRectF(rect)
        bounding_rect = BoundingRectF.fromPoints(self.__points)

        target_rect.setSize(bounding_rect.size().scaled(rect.size(), aspect_ratio_mode))

        # Todo: Alignment
        target_rect.moveCenter(rect.center())

        bounding_polygon = QPolygonF(bounding_rect)
        bounding_polygon.takeLast()

        target_polygon = QPolygonF(target_rect)
        target_polygon.takeLast()

        return QTransform.quadToQuad(bounding_polygon, target_polygon)

    def fitInRect(self, rect, aspect_ratio_mode=Qt.KeepAspectRatio):
        transform = self.transformToRect(rect, aspect_ratio_mode)
        self.__points = tuple(transform.map(point) for point in self.__points)

    def fittedInRect(self, rect, aspect_ratio_mode=Qt.KeepAspectRatio):
        new = self.copy()
        new.fitInRect(rect, aspect_ratio_mode)
        return new

    def painterPath(self):
        path = QPainterPath(self.__points[0])

        for point in self.__points:
            path.lineTo(point)
        path.closeSubpath()

        return path

    @staticmethod
    def fromFile(file_path, allow_excluded=False):
        shape = NodeShape()

        try:
            with open(file_path) as file:
                shape_data = json.load(file)
        except IOError:
            return shape

        if 'name' in shape_data:
            shape.__name = shape_data['name']
        else:
            shape.__name, _ = os.path.splitext(os.path.basename(file_path))

        if not allow_excluded and shape.__name in EXCLUDED_SHAPES:
            return shape

        if not shape_data or 'outline' not in shape_data:
            return shape

        shape.__points = tuple(QPointF(x, -y) for x, y in shape_data['outline'])

        shape.__valid = True
        return shape

    @staticmethod
    def fromName(name, allow_excluded=False):
        if not name:
            return NodeShape()

        name = name.replace(' ', '_').lower()

        if allow_excluded and name in EXCLUDED_SHAPES:
            return NodeShape()

        file_name = name + '.json'
        shape_files = hou.findFilesWithExtension('json', 'config/NodeShapes')
        for file_path in shape_files:
            if file_name in file_path.lower():
                return NodeShape.fromFile(file_path)
        return NodeShape()

    @staticmethod
    def isValidShape(name):
        name = name.replace(' ', '_').lower()

        if name in EXCLUDED_SHAPES:
            return False

        file_name = name + '.json'
        shape_files = hou.findFilesWithExtension('json', 'config/NodeShapes')
        for file_path in shape_files:
            if file_name in file_path.lower():
                return True
        return False
