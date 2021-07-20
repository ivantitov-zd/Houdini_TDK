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
    from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy,
                                 QPushButton, QFileDialog, QAction, QAbstractItemView)
    from PyQt5.QtGui import QKeySequence
    from PyQt5.QtCore import Qt
except ImportError:
    from PySide2.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy,
                                   QPushButton, QFileDialog, QAction, QAbstractItemView)
    from PySide2.QtGui import QKeySequence
    from PySide2.QtCore import Qt

import hou

from ..fuzzy_proxy_model import FuzzyProxyModel
from ..widgets import InputField, Slider
from .model import IconListModel
from .view import IconListView


class IconListWindow(QDialog):
    def __init__(self, parent=None):
        super(IconListWindow, self).__init__(parent, Qt.Window)

        self.setWindowTitle('TDK: Icons')
        self.setWindowIcon(hou.qt.Icon('MISC_m', 32, 32))
        self.resize(820, 500)

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(4)
        main_layout.addLayout(top_layout)

        # Icon list
        self.icon_list_model = IconListModel(self)

        self._filter_proxy_model = FuzzyProxyModel(self)
        self._filter_proxy_model.setDynamicSortFilter(True)
        self._filter_proxy_model.sort(0, Qt.DescendingOrder)
        self._filter_proxy_model.setSourceModel(self.icon_list_model)

        self._icon_list_view = IconListView()
        self._icon_list_view.setModel(self._filter_proxy_model)
        self._icon_list_view.itemDoubleClicked.connect(self.accept)
        main_layout.addWidget(self._icon_list_view)

        # Search
        self._search_field = InputField()
        self._search_field.setPlaceholderText('Search...')
        self._search_field.textChanged.connect(self._filter_proxy_model.setPattern)
        top_layout.addWidget(self._search_field)

        # Scale
        self._slider = Slider(Qt.Horizontal)
        self._slider.setFixedWidth(120)
        self._slider.setDefaultValue(64)
        self._slider.setRange(48, 128)
        self._slider.valueChanged.connect(self.setIconSize)
        self._icon_list_view.iconSizeChanged.connect(lambda size: self.setIconSize(size.width()))
        top_layout.addWidget(self._slider)

        # Buttons
        buttons_layout = QHBoxLayout()
        main_layout.addLayout(buttons_layout)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored)
        buttons_layout.addSpacerItem(spacer)

        self._ok_button = QPushButton('OK')
        self._ok_button.setVisible(False)
        self._ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self._ok_button)

        self._cancel_button = QPushButton('Cancel')
        self._cancel_button.setVisible(False)
        self._cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self._cancel_button)

        # Menu
        self._menu = None
        self._copy_name_action = None
        self._copy_file_name_action = None
        self._copy_image_action = None
        self._save_image_action = None

        self._createActions()

        self._icon_list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._icon_list_view.customContextMenuRequested.connect(self.showContextMenu)

        self.setIconSize(64)

    def setIconSize(self, size):
        size = min(max(size, 48), 128)
        self._slider.setToolTip('Size: ' + str(size))
        self._slider.setValue(size)
        self._icon_list_view.setIconSize(size)

    def copySelectedIconName(self):
        names = []
        for index in self._icon_list_view.selectedIndexes():
            names.append(index.data(Qt.ToolTipRole))

        QApplication.clipboard().setText('\n'.join(name[:-4] for name in names))

    def copySelectedIconFileName(self):
        names = []
        for index in self._icon_list_view.selectedIndexes():
            names.append(index.data(Qt.ToolTipRole))

        QApplication.clipboard().setText('\n'.join(names))

    def _selectedImage(self):
        indexes = self._icon_list_view.selectedIndexes()
        if len(indexes) == 1:
            name = indexes[0].data(Qt.UserRole)
            icon_size = self._icon_list_view.model().iconSize()
            return hou.qt.Icon(name, icon_size, icon_size).pixmap(icon_size, icon_size)

    def copySelectedIcon(self):
        image = self._selectedImage()
        if image:
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(image)

    def saveSelectedIcon(self):
        indexes = self._icon_list_view.selectedIndexes()

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
        self._copy_name_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self._icon_list_view.addAction(self._copy_name_action)

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
        selection_size = len(self._icon_list_view.selectedIndexes())

        if selection_size == 0:
            self._menu.setEnabled(False)
        else:
            self._menu.setEnabled(True)

        if selection_size == 1:
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

    def enableDialogMode(self):
        self._icon_list_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self._icon_list_view.enableDoubleClickedSignal()
        self._ok_button.setVisible(True)
        self._cancel_button.setVisible(True)

    @classmethod
    def getIconName(cls, parent=hou.qt.mainWindow(), title='Icons', name=None):
        window = IconListWindow(parent)
        window.setWindowTitle('TDK: ' + title)
        window.enableDialogMode()

        if name:
            model = window._icon_list_view.model()
            for row in range(model.rowCount()):
                index = model.index(row, 0)
                if index.data(Qt.UserRole) == name + '.svg':
                    window._icon_list_view.setCurrentIndex(index)
                    break

        if window.exec_() and window._icon_list_view.currentIndex().isValid():
            return window._icon_list_view.currentIndex().data(Qt.UserRole).replace('.svg', '')


def findIcon(**kwargs):
    window = IconListWindow(hou.qt.mainWindow())
    window.show()
