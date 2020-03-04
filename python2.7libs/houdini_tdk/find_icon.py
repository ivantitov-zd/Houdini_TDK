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


class FilterField(QLineEdit):
    # Signals
    accepted = Signal()

    def __init__(self):
        super(FilterField, self).__init__()

        self.setPlaceholderText('Type to Filter...')

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self.clear()
        elif key == Qt.Key_Enter or key == Qt.Key_Return:
            self.accepted.emit()
        else:
            super(FilterField, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton and \
                event.modifiers() == Qt.ControlModifier:
            self.clear()
        super(FilterField, self).mousePressEvent(event)


class IconCache:
    default_icon = hou.qt.Icon('MISC_tier_one', 48, 48)
    data = {}

    @staticmethod
    def icon(name):
        if name not in IconCache.data:
            try:
                IconCache.data[name] = hou.qt.Icon(name, 48, 48)
            except hou.OperationFailed:
                IconCache.data[name] = IconCache.default_icon
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

        self.__filter_pattern = ''
        self.setDynamicSortFilter(True)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)

    def setFilterPattern(self, pattern):
        self.beginResetModel()
        if self.filterCaseSensitivity() == Qt.CaseInsensitive:
            self.__filter_pattern = pattern.lower()
        else:
            self.__filter_pattern = pattern
        self.endResetModel()

    def filterAcceptsRow(self, source_row, source_parent):
        source_model = self.sourceModel()
        text = source_model.data(source_model.index(source_row, 0, source_parent), Qt.UserRole)
        matches, weight = fuzzyMatch(self.__filter_pattern, text if self.filterCaseSensitivity() == Qt.CaseSensitive else text.lower())
        return matches

    def lessThan(self, source_left, source_right):
        text1 = source_left.data(Qt.UserRole)
        _, weight1 = fuzzyMatch(self.__filter_pattern, text1 if self.filterCaseSensitivity() == Qt.CaseSensitive else text1.lower())

        text2 = source_right.data(Qt.UserRole)
        _, weight2 = fuzzyMatch(self.__filter_pattern, text2 if self.filterCaseSensitivity() == Qt.CaseSensitive else text2.lower())

        return weight1 < weight2


class IconListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(IconListModel, self).__init__(parent)

        # Data
        icon_index_file = hou.expandString('$HFS/houdini/config/Icons/SVGIcons.index')
        self.__data = sorted(hou.loadIndexDataFromFile(icon_index_file).keys())

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
        self.setContextMenuPolicy(Qt.CustomContextMenu)


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


def findIcon(**kwargs):
    window = FindIconWindow(hou.qt.mainWindow())
    window.show()
