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
    from PyQt5.QtCore import QAbstractItemModel, QModelIndex
    from PyQt5.QtGui import Qt
except ImportError:
    from PySide2.QtCore import QAbstractItemModel, QModelIndex
    from PySide2.QtGui import Qt

from .gather import gatherNetworkStats, CounterGroup, Counter


class NetworkStatsModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(NetworkStatsModel, self).__init__(parent)

        self._data = ()

    def updateData(self, node):
        self.beginResetModel()
        self._data = gatherNetworkStats(node)
        self.endResetModel()

    def hasChildren(self, parent):
        if not parent.isValid():
            return True

        return isinstance(parent.internalPointer(), CounterGroup)

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        item = index.internalPointer()
        if item.parent is None:
            return QModelIndex()

        if item.parent.parent is None:
            parent_item_index = self._data.index(item.parent)
        else:
            parent_item_index = item.parent.children.index(item)

        return self.createIndex(parent_item_index, 0, item.parent)

    def columnCount(self, parent):
        return 2

    def rowCount(self, parent):
        if not parent.isValid():
            return len(self._data)

        parent_item = parent.internalPointer()
        return len(parent_item.children)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            item = self._data[row]
        else:
            parent_item = parent.internalPointer()
            item = parent_item.children[row]

        return self.createIndex(row, column, item)

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():
            return

        column = index.column()
        item = index.internalPointer()

        if column == 0:
            if role == Qt.DisplayRole:
                return item.name
        elif column == 1 and isinstance(item, Counter):
            if role == Qt.DisplayRole:
                return item.value
