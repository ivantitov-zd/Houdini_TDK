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


class HDADefinitionProxy(object):
    def __init__(self, definition):
        self.definition = definition
        self._name = definition.nodeTypeName()
        self._label = definition.description()
        self._icon = definition.icon()
        self._library_file_path = definition.libraryFilePath()

    def nodeTypeName(self):
        return self._name

    def description(self):
        return self._label

    def icon(self):
        return self._icon

    def libraryFilePath(self):
        return self._library_file_path

    def __getattr__(self, attr_name):
        return self.definition.__getattribute__(attr_name)


class OperatorManagerLibraryModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(OperatorManagerLibraryModel, self).__init__(parent)

        self._libraries = ()
        self._definitions = {}

    def updateData(self):
        self.beginResetModel()

        single_def_libs = {}
        multiple_def_libs = []
        self._definitions = {}

        for category in hou.nodeTypeCategories().values():
            for node_type in category.nodeTypes().values():
                definition = node_type.definition()
                if definition is None:
                    continue

                lib_path = definition.libraryFilePath()
                if lib_path not in self._definitions:
                    definitions = hou.hda.definitionsInFile(lib_path)
                    if len(definitions) == 1:
                        _, _, name, version = definitions[0].nodeType().nameComponents()
                        single_def_libs[lib_path] = name + version
                    else:
                        multiple_def_libs.append(lib_path)
                    self._definitions[lib_path] = map(HDADefinitionProxy, definitions)

        single_def_libs = tuple(sorted(single_def_libs.keys(), key=single_def_libs.get))
        multiple_def_libs = tuple(sorted(multiple_def_libs))
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
            return len(self._definitions[parent.internalPointer()])

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
            return self.createIndex(self._definitions[lib_path].index(item), 0, lib_path)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            return self.createIndex(row, column, self._libraries[row])
        else:
            current_lib_path = parent.internalPointer()
            return self.createIndex(row, column, self._definitions[current_lib_path][row])

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():
            return

        if role == Qt.UserRole:
            return index.internalPointer()

        column = index.column()
        if column == 0:
            if not index.parent().isValid():
                lib_path = index.internalPointer()
                if role == TextRole:
                    return lib_path
                elif role == Qt.ToolTipRole:
                    return lib_path
                elif role == Qt.DecorationRole:
                    return INSTALLED_ICON
            else:
                definition = index.internalPointer()
                if role in (Qt.DisplayRole, TextRole):
                    return definition.description()
                elif role == Qt.DecorationRole:
                    try:
                        return hou.qt.Icon(definition.icon(), ICON_SIZE, ICON_SIZE)
                    except hou.OperationFailed:
                        return EMPTY_ICON
        elif column == 1:
            if index.parent().isValid():
                definition = index.internalPointer()
                if role in (Qt.DisplayRole, TextRole):
                    return definition.nodeTypeName()
