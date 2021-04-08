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

ICON_SIZE = 16
INSTALLED_ICON = hou.qt.Icon('TOP_status_cooked', ICON_SIZE, ICON_SIZE)
NOT_INSTALLED_ICON = hou.qt.Icon('TOP_status_error', ICON_SIZE, ICON_SIZE)
EMPTY_ICON = hou.qt.Icon('MISC_empty', ICON_SIZE, ICON_SIZE)

TextRole = Qt.UserRole + 1


class NodeTypeProxy(object):
    __slots__ = 'node_type', '_name', '_name_with_category', '_label', '_icon', '_library_file_path'

    def __init__(self, node_type):
        self.node_type = node_type
        self._name = node_type.name()
        self._name_with_category = node_type.nameWithCategory()
        self._label = node_type.description()
        self._icon = node_type.icon()
        if node_type.definition() is None:
            self._library_file_path = 'Internal'
        else:
            self._library_file_path = node_type.definition().libraryFilePath()

    def name(self):
        return self._name

    def nameWithCategory(self):
        return self._name_with_category

    def description(self):
        return self._label

    def icon(self):
        return self._icon

    def libraryFilePath(self):
        return self._library_file_path

    def __getattr__(self, attr_name):
        return self.node_type.__getattribute__(attr_name)


class OperatorManagerLibraryModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(OperatorManagerLibraryModel, self).__init__(parent)

        self._libraries = ()
        self._types = {}

    def updateData(self):
        self.beginResetModel()

        single_def_libs = {}
        multiple_def_libs = []
        self._types = {}
        internal_types = []

        for category in hou.nodeTypeCategories().values():
            for node_type in category.nodeTypes().values():
                definition = node_type.definition()
                if definition is None:
                    internal_types.append(NodeTypeProxy(node_type))
                    continue

                lib_path = definition.libraryFilePath()
                if lib_path not in self._types:
                    definitions = hou.hda.definitionsInFile(lib_path)
                    if len(definitions) == 1:
                        single_def_libs[lib_path] = definitions[0].nodeType().nameWithCategory()
                    else:
                        multiple_def_libs.append(lib_path)
                    self._types[lib_path] = tuple(sorted((NodeTypeProxy(d.nodeType()) for d in definitions),
                                                         key=lambda tp: tp.nameWithCategory()))

        single_def_libs = tuple(sorted(single_def_libs.keys(), key=single_def_libs.get))
        self._types['Internal'] = tuple(sorted(internal_types,
                                               key=lambda t: t.nameComponents()[2] + t.nameWithCategory()))
        multiple_def_libs = tuple(sorted(multiple_def_libs)) + ('Internal',)
        self._libraries = single_def_libs + multiple_def_libs

        self.endResetModel()

    def hasChildren(self, parent):
        if not parent.isValid():
            return bool(self._libraries)
        elif isinstance(parent.internalPointer(), basestring):
            return True

        return False

    def rowCount(self, parent):
        if not parent.isValid():
            return len(self._libraries)
        else:
            return len(self._types[parent.internalPointer()])

    def columnCount(self, parent):
        return 2

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        item = index.internalPointer()
        if isinstance(item, basestring):
            return QModelIndex()
        else:
            lib_path = item.libraryFilePath()
            return self.createIndex(self._types[lib_path].index(item), 0, lib_path)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            return self.createIndex(row, column, self._libraries[row])
        else:
            current_lib_path = parent.internalPointer()
            return self.createIndex(row, column, self._types[current_lib_path][row])

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():
            return

        item_data = index.internalPointer()

        column = index.column()
        if column == 0:
            if not index.parent().isValid():
                library_path = item_data
                if role == Qt.DisplayRole:
                    return os.path.dirname(library_path)
                elif role == TextRole:
                    return library_path
                elif role == Qt.ToolTipRole:
                    return library_path
                elif role == Qt.DecorationRole:
                    return INSTALLED_ICON
                elif role == Qt.UserRole:
                    return library_path
            else:
                node_type_proxy = item_data
                if role in (Qt.DisplayRole, TextRole):
                    return node_type_proxy.description()
                elif role == Qt.DecorationRole:
                    try:
                        return hou.qt.Icon(node_type_proxy.icon(), ICON_SIZE, ICON_SIZE)
                    except hou.OperationFailed:
                        return EMPTY_ICON
                elif role == Qt.UserRole:
                    return node_type_proxy.node_type
        elif column == 1:
            if not index.parent().isValid():
                library_path = item_data
                if role == Qt.DisplayRole:
                    return os.path.basename(library_path)
                elif role == Qt.ToolTipRole:
                    return library_path
                elif role == Qt.UserRole:
                    return library_path
            else:
                node_type_proxy = item_data
                if role in (Qt.DisplayRole, TextRole):
                    return node_type_proxy.nameWithCategory()
                elif role == Qt.UserRole:
                    return node_type_proxy.node_type
