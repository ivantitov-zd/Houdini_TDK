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


class NodeProxy(object):
    __slots__ = 'node', '_name', '_path'

    def __init__(self, node):
        self.node = node
        self._name = node.name()
        self._path = node.path()

    def exists(self):
        return bool(hou.nodeBySessionId(self.node.sessionId()))

    def name(self):
        return self._name

    def path(self):
        return self._path

    def __getattr__(self, attr_name):
        return self.node.__getattribute__(attr_name)


class UsageListModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(UsageListModel, self).__init__(parent)

        self._definition = None
        self._nodes = ()

    def updateData(self):
        if not self._definition:
            return

        self.beginResetModel()

        nodes = sorted(map(NodeProxy, self._definition.nodeType().instances()),
                       key=lambda node: node.path().count('/'))
        self._nodes = tuple(nodes)

        self.endResetModel()

    def setDefinition(self, definition):
        self._definition = definition
        self.updateData()

    def hasChildren(self, parent):
        if parent.isValid():
            return False

        return True

    def rowCount(self, parent):
        return len(self._nodes)

    def columnCount(self, parent):
        return 2

    def headerData(self, section, orientation, role):
        names = ('Name', 'Path')
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return names[section]

    def parent(self, index):
        return QModelIndex()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        return self.createIndex(row, column, self._nodes[row])

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():
            return

        node = index.internalPointer()

        if not node.exists():
            if role == Qt.FontRole:
                font = QFont()
                font.setStrikeOut(True)
                return font
            elif role == Qt.ToolTipRole:
                return 'Node was deleted.'

        if role == Qt.UserRole:
            return node.path()
        elif role == Qt.UserRole + 1:
            return node

        column = index.column()
        if column == 0:
            if role == Qt.DisplayRole:
                return node.name()
        elif column == 1:
            if role == Qt.DisplayRole:
                return node.path()
