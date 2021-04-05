"""
Tool Development Kit for SideFX Houdini
Copyright (C) 2021 Ivan Titov

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

ICON_SIZE = 16
EMPTY_ICON = hou.qt.Icon('MISC_empty', ICON_SIZE, ICON_SIZE)

TextRole = Qt.UserRole + 1


class OperatorManagerNodeTypeModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(OperatorManagerNodeTypeModel, self).__init__(parent)

        self._names = ()
        self._types = {}

    def updateData(self):
        self.beginResetModel()

        node_types = {}

        for category in hou.nodeTypeCategories().values():
            for node_type in category.nodeTypes().values():
                if node_type.definition() is None:
                    continue

                _, _, name, _ = node_type.nameComponents()
                if name not in node_types:
                    node_types[name] = [node_type]
                else:
                    node_types[name].append(node_type)

        self._names = tuple(sorted(node_types.keys()))
        self._types = {
            name: tuple(sorted(node_types[name], key=lambda t: t.name()))
            for name in node_types.keys()
        }

        self.endResetModel()

    def hasChildren(self, parent):
        if not parent.isValid():
            return bool(self._names)
        elif isinstance(parent.internalPointer(), basestring):
            return True

        return False

    def rowCount(self, parent):
        if not parent.isValid():
            return len(self._names)
        else:
            return len(self._types[parent.internalPointer()])

    def columnCount(self, parent):
        return 4

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        item = index.internalPointer()
        if isinstance(item, basestring):
            return QModelIndex()
        else:
            type_name = item.nameComponents()[2]
            return self.createIndex(self._types[type_name].index(item), 0, type_name)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            return self.createIndex(row, column, self._names[row])
        else:
            type_name = parent.internalPointer()
            return self.createIndex(row, column, self._types[type_name][row])

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():
            return

        item_data = index.internalPointer()

        if role == Qt.UserRole:
            return item_data

        column = index.column()

        if not isinstance(item_data, hou.NodeType):
            type_name = item_data
            if column == 0:
                if role == Qt.DisplayRole:
                    return type_name
        else:
            node_type = item_data
            if column == 0:
                if role == Qt.DisplayRole:
                    return node_type.description()
                elif role == Qt.DecorationRole:
                    try:
                        return hou.qt.Icon(node_type.icon(), ICON_SIZE, ICON_SIZE)
                    except hou.OperationFailed:
                        return EMPTY_ICON
            elif column == 1:
                if role == Qt.DisplayRole:
                    namespace = node_type.nameComponents()[1]
                    return namespace or '-'
            elif column == 2:
                if role == Qt.DisplayRole:
                    version = node_type.nameComponents()[3]
                    return version or '-'
            elif column == 3:
                if role == Qt.DisplayRole:
                    return node_type.definition().libraryFilePath()
