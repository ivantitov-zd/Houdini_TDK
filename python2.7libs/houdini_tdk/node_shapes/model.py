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

from .node_shape import NodeShape


class NodeShapeListModel(QAbstractListModel):
    # Roles
    ShapeNameRole = Qt.UserRole + 1
    ShapeRole = Qt.UserRole + 2

    def __init__(self, parent=None):
        super(NodeShapeListModel, self).__init__(parent)

        self.shapes = ()

    def updateNodeShapeList(self):
        self.beginResetModel()

        shapes = []
        shape_files = hou.findFilesWithExtension('json', 'config/NodeShapes')
        for file_path in shape_files:
            shape = NodeShape.fromFile(file_path)
            if shape.isValid():
                shapes.append(shape)

        self.shapes = tuple(shapes)
        self.endResetModel()

    def rowCount(self, parent):
        return len(self.shapes)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        return self.createIndex(row, column, self.shapes[row])

    def data(self, index, role):
        if not index.isValid():
            return

        shape = index.internalPointer()

        if role == Qt.DisplayRole:
            return shape.name().replace('_', ' ').title()
        elif role == Qt.ToolTipRole:
            return shape.name()
        elif role == NodeShapeListModel.ShapeNameRole:
            return shape.name()
        elif role == NodeShapeListModel.ShapeRole:
            return shape
