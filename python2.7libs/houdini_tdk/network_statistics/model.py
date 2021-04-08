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

from .gather import gatherNetworkStats


class StatItem:
    def __init__(self, text=None, value=None, child_items=()):
        self.text = text
        self.value = str(value) if value is not None else None
        self._index = None
        self.parent = None
        self._child_items = child_items or ()
        for index, item in enumerate(self._child_items):
            item.index = index
            item.parent = self

    def __getitem__(self, item):
        return self._child_items[item]

    def __len__(self):
        return len(self._child_items)


class NetworkStatsModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(NetworkStatsModel, self).__init__(parent)

        self._data = StatItem()

    def updateData(self, node):
        self.beginResetModel()
        data = gatherNetworkStats(node)
        self._data = StatItem(None, None,
                              [
                                  StatItem('Nodes', None,
                                           [
                                               StatItem('Total', data['nodes']['total']),
                                               StatItem('Subnetworks', data['nodes']['subnetworks']),
                                               StatItem('Inside Locked', data['nodes']['inside_locked']),
                                               StatItem('Maximum Depth', data['nodes']['max_depth'])
                                           ]),
                                  StatItem('Parameters', None,
                                           [
                                               StatItem('Animated', data['parms']['animated']),
                                               StatItem('Links to', None,
                                                        [
                                                            StatItem('parameters', data['parms']['links_to']['parms']),
                                                            StatItem('nodes', data['parms']['links_to']['nodes']),
                                                            StatItem('folders', data['parms']['links_to']['folders']),
                                                            StatItem('files', data['parms']['links_to']['files']),
                                                            StatItem('web', data['parms']['links_to']['web'])
                                                        ])
                                           ])
                                  # Todo: code stats section
                              ])
        self.endResetModel()

    def hasChildren(self, parent):
        if not parent.isValid():
            return True

        return bool(parent.internalPointer())

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        item = index.internalPointer()
        if item.text is None:
            return QModelIndex()

        return self.createIndex(item.index, 0, item.parent)

    def columnCount(self, parent):
        return 2

    def rowCount(self, parent):
        if not parent.isValid():
            return len(self._data)

        item = parent.internalPointer()
        return len(item)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            item = self._data[row]
        else:
            item = parent.internalPointer()[row]

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
                return item.text
        elif column == 1:
            if role == Qt.DisplayRole:
                return item.value
        # Todo: column 3 - percentage
