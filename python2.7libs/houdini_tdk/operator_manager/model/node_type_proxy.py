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
