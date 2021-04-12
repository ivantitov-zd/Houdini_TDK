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

from operator import attrgetter

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

from .node_type_proxy import NodeTypeProxy

ICON_SIZE = 16
EMPTY_ICON = hou.qt.Icon('MISC_empty', ICON_SIZE, ICON_SIZE)


class TypeNameItem(object):
    __slots__ = 'category_name', 'type_name',

    def __init__(self, category_name, type_name):
        self.category_name = category_name
        self.type_name = type_name

    def __eq__(self, other):
        return other == self.type_name


class OperatorManagerNodeTypeModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(OperatorManagerNodeTypeModel, self).__init__(parent)

        self._category_names = ()
        self._type_names = {}
        self._types = {}

    def updateData(self):
        self.beginResetModel()

        types = {}

        for category_name, category in hou.nodeTypeCategories().items():
            category_types = types[category_name] = {}
            for node_type in category.nodeTypes().values():
                type_name = node_type.nameComponents()[2]
                if type_name not in category_types:
                    category_types[type_name] = [node_type]
                else:
                    category_types[type_name].append(node_type)

        # Remove empty categories
        for category_name in tuple(types.keys()):
            if len(types[category_name]) == 0:
                del types[category_name]

        self._category_names = tuple(sorted(types.keys()))

        self._type_names = {}
        for category_name in self._category_names:
            self._type_names[category_name] = tuple(TypeNameItem(category_name, type_name)
                                                    for type_name in sorted(types[category_name].keys()))

            types[category_name] = {
                type_name: tuple(sorted(map(NodeTypeProxy, node_types), key=attrgetter('name')))
                for type_name, node_types in types[category_name].items()
            }

        self._types = types

        self.endResetModel()

    def hasChildren(self, parent):
        if not parent.isValid():
            return bool(self._category_names)
        elif isinstance(parent.internalPointer(), (basestring, TypeNameItem)):
            return True
        else:
            return False

    def rowCount(self, parent):
        if not parent.isValid():
            return len(self._category_names)
        elif isinstance(parent.internalPointer(), basestring):
            category_name = parent.internalPointer()
            return len(self._type_names[category_name])
        elif isinstance(parent.internalPointer(), TypeNameItem):
            type_name_item = parent.internalPointer()
            return len(self._types[type_name_item.category_name][type_name_item.type_name])
        else:
            return 0

    def columnCount(self, parent):
        return 4

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        item_data = index.internalPointer()

        if isinstance(item_data, basestring):
            return QModelIndex()
        elif isinstance(item_data, TypeNameItem):
            return self.createIndex(self._type_names[item_data.category_name].index(item_data.type_name), 0,
                                    item_data.category_name)
        elif isinstance(item_data, NodeTypeProxy):
            node_type = item_data
            category_name = node_type.category().name()
            type_name = node_type.nameComponents()[2]
            type_name_index = self._type_names[category_name].index(type_name)
            type_name_item = self._type_names[category_name][type_name_index]
            return self.createIndex(type_name_index, 0, type_name_item)
        else:
            return QModelIndex()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            return self.createIndex(row, column, self._category_names[row])
        elif isinstance(parent.internalPointer(), basestring):
            category_name = parent.internalPointer()
            type_name_item = self._type_names[category_name][row]
            return self.createIndex(row, column, type_name_item)
        elif isinstance(parent.internalPointer(), TypeNameItem):
            type_name_item = parent.internalPointer()
            return self.createIndex(row, column,
                                    self._types[type_name_item.category_name][type_name_item.type_name][row])
        return QModelIndex()

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():
            return

        item_data = index.internalPointer()

        if role == Qt.UserRole:
            if isinstance(item_data, NodeTypeProxy):
                item_data = item_data.node_type
            return item_data

        column = index.column()

        if isinstance(item_data, basestring):
            if item_data in self._category_names:
                category_name = item_data
                if column == 0:
                    if role == Qt.DisplayRole:
                        return category_name
        elif isinstance(item_data, TypeNameItem):
            if column == 0:
                if role == Qt.DisplayRole:
                    return item_data.type_name
        elif isinstance(item_data, NodeTypeProxy):
            node_type_proxy = item_data
            if column == 0:
                if role == Qt.DisplayRole:
                    return node_type_proxy.description()
                elif role == Qt.DecorationRole:
                    try:
                        return hou.qt.Icon(node_type_proxy.icon(), ICON_SIZE, ICON_SIZE)
                    except hou.OperationFailed:
                        return EMPTY_ICON
            elif column == 1:
                namespace = node_type_proxy.nameComponents()[1]
                if role == Qt.DisplayRole:
                    return namespace or '-'
                elif role == Qt.TextAlignmentRole:
                    return Qt.AlignLeft | Qt.AlignVCenter if namespace else Qt.AlignCenter
            elif column == 2:
                version = node_type_proxy.nameComponents()[3]
                if role == Qt.DisplayRole:
                    return version or '-'
                elif role == Qt.TextAlignmentRole:
                    return Qt.AlignLeft | Qt.AlignVCenter if version else Qt.AlignCenter
            elif column == 3:
                if role == Qt.DisplayRole:
                    return node_type_proxy.libraryFilePath()
