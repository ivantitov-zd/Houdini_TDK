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

from __future__ import print_function

import os
import re
from datetime import datetime

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

    Signal = pyqtSignal
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *


class BackupListModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(BackupListModel, self).__init__(parent)

        self._library = ''
        self._backup_dir = ''
        self._backup_file_names = ()
        self._backup_data = {}

    def updateData(self):
        self.beginResetModel()

        path, library_file_name = os.path.split(self._library)
        backup_dir = os.path.join(path, 'backup').replace('\\', '/')
        backup_prefix = library_file_name[:-4]  # Remove extension .hda
        backup_pattern = re.compile(re.escape(backup_prefix) + r'_bak\d+\.hda')

        backup_data = {}
        for file_name in os.listdir(backup_dir):
            if backup_pattern.match(file_name):
                file_path = os.path.join(backup_dir, file_name)
                file_stats = os.stat(file_path)
                timestamp = file_stats.st_mtime
                f_timestamp = datetime.fromtimestamp(timestamp).strftime('%H:%M  %d %b %Y')
                file_size = '{:.3f} MB'.format(file_stats.st_size / 1024. / 1024.)

                backup_data[file_name] = timestamp, f_timestamp, file_size

        self._backup_dir = backup_dir
        self._backup_file_names = tuple(sorted(backup_data.keys(), key=lambda key: backup_data[key][0], reverse=True))
        self._backup_data = backup_data

        self.endResetModel()

    def setLibrary(self, library_path):
        self._library = library_path
        self.updateData()

    def hasChildren(self, parent):
        if parent.isValid():
            return False

        return True

    def rowCount(self, parent):
        return len(self._backup_file_names)

    def columnCount(self, parent):
        return 3

    def headerData(self, section, orientation, role):
        names = ('Name', 'Created', 'Size')
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return names[section]

    def parent(self, index):
        return QModelIndex()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        return self.createIndex(row, column, self._backup_data[self._backup_file_names[row]])

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():
            return

        _, f_timestamp, file_size = index.internalPointer()

        column = index.column()
        if column == 0:
            if role == Qt.DisplayRole:
                return self._backup_file_names[index.row()]
        elif column == 1:
            if role == Qt.DisplayRole:
                return f_timestamp
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        elif column == 2:
            if role == Qt.DisplayRole:
                return file_size
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
