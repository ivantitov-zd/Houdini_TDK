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


class NodeShape(QPainterPath):
    def __init__(self):
        super(NodeShape, self).__init__()

        self.__valid = False
        self.__name = None

    def isValid(self):
        return self.__valid

    def __bool__(self):
        return self.__valid

    def name(self):
        return self.__name

    def draw(self, device, painter=None, pen=None, brush=None, transform=None):
        p = painter or QPainter(device)
        p.save()

        if pen:
            p.setPen(pen)

        if brush:
            p.setBrush(brush)

        if transform:
            p.setTransform(transform)

        p.drawPath(self)
        p.restore()

    @staticmethod
    def fromFile(file_path):
        shape = NodeShape()

        try:
            with open(file_path) as file:
                shape_data = json.load(file)
        except IOError:
            return shape

        if not shape_data or 'outline' not in shape_data:
            return shape

        start_x, start_y = shape_data['outline'][0]
        start_x *= 100
        start_y *= -100
        shape.moveTo(start_x, start_y)

        for x, y in shape_data['outline']:
            shape.lineTo(x * 100, y * -100)
        shape.closeSubpath()

        if 'name' in shape_data:
            shape.__name = shape_data['name']
        else:
            _, file_name = os.path.split(file_path)
            shape.__name, _ = os.path.splitext(file_name)

        shape.__valid = True
        return shape
