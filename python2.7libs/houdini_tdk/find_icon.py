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

from .filter_field import FilterField
from .fuzzy_filter_proxy_model import FuzzyFilterProxyModel

ICON_SIZE = 64


class IconCache:
    # Icons
    DEFAULT_ICON = hou.qt.Icon('MISC_tier_one', ICON_SIZE, ICON_SIZE)

    # Data
    data = {}

    @staticmethod
    def icon(name):
        if name not in IconCache.data:
            try:
                IconCache.data[name] = hou.qt.Icon(name, ICON_SIZE, ICON_SIZE)
            except hou.OperationFailed:
                IconCache.data[name] = IconCache.DEFAULT_ICON
        return IconCache.data[name]


class IconListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(IconListModel, self).__init__(parent)

        # Data
        ICON_INDEX_FILE = hou.expandString('$HFS/houdini/config/Icons/SVGIcons.index')
        self.__data = tuple(sorted(hou.loadIndexDataFromFile(ICON_INDEX_FILE).keys()))

    def rowCount(self, parent):
        return len(self.__data)

    def data(self, index, role):
        icon_name = self.__data[index.row()]
        if role == Qt.DisplayRole:
            label = icon_name.replace('.svg', '')  # VOP_wood.svg -> VOP_wood
            if '_' in label:
                label = ' '.join(label.split('_')[1:]).title()  # VOP_wood -> Wood
            return label
        elif role == Qt.DecorationRole:
            return IconCache.icon(icon_name)
        elif role == Qt.UserRole or role == Qt.ToolTipRole:
            return icon_name

    def indexByKey(self, key):
        for index, name in enumerate(self.__data):
            if name[:-4] == key:
                return self.index(index, 0)

        return QModelIndex()


class IconListView(QListView):
    # Signals
    itemDoubleClicked = Signal(QModelIndex)

    def __init__(self):
        super(IconListView, self).__init__()
        self.setViewMode(QListView.IconMode)
        self.setIconSize(QSize(ICON_SIZE, ICON_SIZE))

        self.setUniformItemSizes(True)
        self.setBatchSize(60)
        self.setLayoutMode(QListView.Batched)

        self.setResizeMode(QListView.Adjust)
        self.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(30)

        self.setSpacing(15)

        # Item Double Clicked
        self._item_double_clicked_signal_enabled = False
        self.doubleClicked.connect(self.__emitItemDoubleClicked)

        # Menu
        self._menu = None
        self._copy_name_action = None
        self._copy_file_name_action = None
        self._copy_image_action = None
        self._save_image_action = None

        self._createActions()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

    def doubleClickedSignalEnabled(self):
        return self._item_double_clicked_signal_enabled

    def enableDoubleClickedSignal(self, enable=True):
        self._item_double_clicked_signal_enabled = enable

    def copySelectedIconName(self):
        names = []
        for index in self.selectedIndexes():
            names.append(index.data(Qt.ToolTipRole))

        QApplication.clipboard().setText('\n'.join(name[:-4] for name in names))

    def copySelectedIconFileName(self):
        names = []
        for index in self.selectedIndexes():
            names.append(index.data(Qt.ToolTipRole))

        QApplication.clipboard().setText('\n'.join(names))

    def _selectedImage(self):
        indexes = self.selectedIndexes()
        if len(indexes) == 1:
            name = indexes[0].data(Qt.UserRole)
            return hou.qt.Icon(name, ICON_SIZE, ICON_SIZE).pixmap(ICON_SIZE, ICON_SIZE)

    def copySelectedIcon(self):
        image = self._selectedImage()
        if image:
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(image)

    def saveSelectedIcon(self):
        indexes = self.selectedIndexes()

        if len(indexes) != 1:
            return

        name = indexes[0].data(Qt.DisplayRole)
        path, _ = QFileDialog.getSaveFileName(self, 'Save image',
                                              name, filter='PNG (*.png)',
                                              initialFilter=name)

        image = self._selectedImage()
        if path and image:
            image.save(path)

    def _createActions(self):
        # Copy Name
        self._copy_name_action = QAction('Copy Name', self)
        self._copy_name_action.triggered.connect(self.copySelectedIconName)
        self._copy_name_action.setShortcut(QKeySequence.Copy)
        self.addAction(self._copy_name_action)

        # Copy File Name
        self._copy_file_name_action = QAction('Copy File Name', self)
        self._copy_file_name_action.triggered.connect(self.copySelectedIconFileName)

        # Copy Image
        self._copy_image_action = QAction('Copy Image...', self)
        self._copy_image_action.triggered.connect(self.copySelectedIcon)

        # Save Image
        self._save_image_action = QAction('Save Image...', self)
        self._save_image_action.triggered.connect(self.saveSelectedIcon)

    def _createContextMenu(self):
        self._menu = hou.qt.Menu()

        self._menu.addAction(self._copy_name_action)
        self._menu.addAction(self._copy_file_name_action)

        self._menu.addSeparator()

        self._menu.addAction(self._copy_image_action)
        self._menu.addAction(self._save_image_action)

    def _updateContextMenu(self):
        selected_indices = self.selectedIndexes()
        if len(selected_indices) == 1:
            self._copy_image_action.setEnabled(True)
            self._save_image_action.setEnabled(True)
        else:
            self._copy_image_action.setEnabled(False)
            self._save_image_action.setEnabled(False)

    def showContextMenu(self, local_pos):
        if not self._menu:
            self._createContextMenu()

        self._updateContextMenu()

        return self._menu.exec_(self.mapToGlobal(local_pos))

    def __emitItemDoubleClicked(self):
        if not self._item_double_clicked_signal_enabled:
            return

        index = self.currentIndex()
        if index.isValid():
            self.itemDoubleClicked.emit(index)


class FindIconDialog(QDialog):
    def __init__(self, parent=None):
        super(FindIconDialog, self).__init__(parent, Qt.Window)

        self.setWindowTitle('TDK: Find Icon')
        self.setWindowIcon(hou.qt.Icon('MISC_m', 32, 32))
        self.resize(820, 500)

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        # Filter
        self.filter_field = FilterField()
        main_layout.addWidget(self.filter_field)

        # Icon List
        self.icon_list_model = IconListModel(self)

        self.filter_proxy_model = FuzzyFilterProxyModel(self)
        self.filter_proxy_model.setSourceModel(self.icon_list_model)
        self.filter_field.textChanged.connect(self.filter_proxy_model.setFilterPattern)

        self.icon_list_view = IconListView()
        self.icon_list_view.setModel(self.filter_proxy_model)
        self.icon_list_view.itemDoubleClicked.connect(self.accept)
        main_layout.addWidget(self.icon_list_view)

        # Buttons
        buttons_layout = QHBoxLayout()
        main_layout.addLayout(buttons_layout)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored)
        buttons_layout.addSpacerItem(spacer)

        self.ok_button = QPushButton('OK')
        self.ok_button.setVisible(False)
        self.ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.setVisible(False)
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Find) or event.key() == Qt.Key_F3:
            self.filter_field.setFocus()
            self.filter_field.selectAll()
        else:
            super(FindIconDialog, self).keyPressEvent(event)

    def enableDialogMode(self):
        self.icon_list_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.icon_list_view.enableDoubleClickedSignal()
        self.ok_button.setVisible(True)
        self.cancel_button.setVisible(True)

    @classmethod
    def getIconName(cls, parent=hou.qt.mainWindow(), title='Find Icon', name=None):
        window = FindIconDialog(parent)
        window.setWindowTitle('TDK: ' + title)
        window.enableDialogMode()

        if name:
            model = window.icon_list_view.model()
            for row in range(model.rowCount()):
                index = model.index(row, 0)
                if index.data(Qt.UserRole) == name + '.svg':
                    window.icon_list_view.setCurrentIndex(index)
                    break

        if window.exec_() and window.icon_list_view.currentIndex().isValid():
            return window.icon_list_view.currentIndex().data(Qt.UserRole).replace('.svg', '')


def findIcon(**kwargs):
    window = FindIconDialog(hou.qt.mainWindow())
    window.show()
