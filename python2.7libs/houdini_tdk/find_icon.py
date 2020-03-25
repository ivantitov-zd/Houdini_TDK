"""
Tool Development Kit for SideFX Houdini
Copyright (C) 2020  Ivan Titov

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

from .filter_field import FilterField


class IconCache:
    # Icons
    DEFAULT_ICON = hou.qt.Icon('MISC_tier_one', 48, 48)

    # Data
    data = {}

    @staticmethod
    def icon(name):
        if name not in IconCache.data:
            try:
                IconCache.data[name] = hou.qt.Icon(name, 48, 48)
            except hou.OperationFailed:
                IconCache.data[name] = IconCache.DEFAULT_ICON
        return IconCache.data[name]


def fuzzyMatch(pattern, word):
    if pattern == word:
        return True, 999999
    weight = 0
    count = 0
    index = 0
    for char in word:
        try:
            if char == pattern[index]:
                count += 1
                index += 1
            elif count != 0:
                weight += count * count
                count = 0
        except IndexError:
            pass
    if count != 0:
        weight += count * count
    if index < len(pattern):
        return False, weight
    return True, weight


class FuzzyFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(FuzzyFilterProxyModel, self).__init__(parent)
        self.setDynamicSortFilter(True)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)

        self.pattern = ''

    def setFilterPattern(self, pattern):
        self.beginResetModel()
        self.pattern = pattern.lower()
        self.endResetModel()

    def filterAcceptsRow(self, source_row, source_parent):
        source_model = self.sourceModel()
        text = source_model.data(source_model.index(source_row, 0, source_parent),
                                 Qt.UserRole)
        matches, weight = fuzzyMatch(self.pattern, text.lower())
        return matches

    def lessThan(self, source_left, source_right):
        text1 = source_left.data(Qt.UserRole)
        _, weight1 = fuzzyMatch(self.pattern, text1.lower())

        text2 = source_right.data(Qt.UserRole)
        _, weight2 = fuzzyMatch(self.pattern, text2.lower())

        return weight1 < weight2


class IconListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(IconListModel, self).__init__(parent)

        # Data
        ICON_INDEX_FILE = hou.expandString('$HFS/houdini/config/Icons/SVGIcons.index')
        self.__data = sorted(hou.loadIndexDataFromFile(ICON_INDEX_FILE).keys())

    def rowCount(self, parent):
        return len(self.__data)

    def data(self, index, role):
        icon_name = self.__data[index.row()]
        if role == Qt.DisplayRole:
            label = icon_name.replace('.svg', '')
            if '_' in label:
                label = ' '.join(label.split('_')[1:]).title()
            return label
        elif role == Qt.DecorationRole:
            return IconCache.icon(icon_name)
        elif role == Qt.UserRole or role == Qt.ToolTipRole:
            return icon_name


class IconListView(QListView):
    def __init__(self):
        super(IconListView, self).__init__()
        self.setViewMode(QListView.IconMode)
        self.setResizeMode(QListView.Adjust)
        self.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(30)
        self.setSpacing(15)
        self.setIconSize(QSize(48, 48))
        self.setUniformItemSizes(True)

        # Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        self.menu = QMenu(self)
        self.menu.addAction('Copy', self.copySelectedIconName, QKeySequence.Copy)

        self.customContextMenuRequested.connect(self.showMenu)

    def copySelectedIconName(self):
        names = []
        for index in self.selectedIndexes():
            names.append(index.data(Qt.ToolTipRole))
        QApplication.clipboard().setText('\n'.join(names))

    def showMenu(self, pos):
        if self.selectedIndexes():
            self.menu.exec_(self.mapToGlobal(pos))

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Copy):
            self.copySelectedIconName()
        else:
            super(IconListView, self).keyPressEvent(event)


class FindIconWindow(QWidget):
    def __init__(self, parent=None):
        super(FindIconWindow, self).__init__(parent, Qt.Window)

        self.setWindowTitle('TDK: Find Icon')
        self.resize(820, 500)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Filter
        self.filter_field = FilterField()
        layout.addWidget(self.filter_field)

        # Icon List
        self.icon_list_model = IconListModel(self)

        self.filter_proxy_model = FuzzyFilterProxyModel(self)
        self.filter_proxy_model.setSourceModel(self.icon_list_model)
        self.filter_field.textChanged.connect(self.filter_proxy_model.setFilterPattern)

        self.icon_list_view = IconListView()
        self.icon_list_view.setModel(self.filter_proxy_model)
        layout.addWidget(self.icon_list_view)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Find) or event.key() == Qt.Key_F3:
            self.filter_field.setFocus()
            self.filter_field.selectAll()
        else:
            super(FindIconWindow, self).keyPressEvent(event)


def findIcon(**kwargs):
    window = FindIconWindow(hou.qt.mainWindow())
    window.show()
