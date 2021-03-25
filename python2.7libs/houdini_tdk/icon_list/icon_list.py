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

from ..fuzzy_proxy_model import FuzzyProxyModel
from ..widgets import FilterField, Slider
from .icon_list_model import IconListModel
from .icon_list_view import IconListView


class IconListDialog(QDialog):
    def __init__(self, parent=None):
        super(IconListDialog, self).__init__(parent, Qt.Window)

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

        # Icon List
        self.icon_list_model = IconListModel(self)

        self.filter_proxy_model = FuzzyProxyModel(self)
        self.filter_proxy_model.setDynamicSortFilter(True)
        self.filter_proxy_model.sort(0, Qt.DescendingOrder)
        self.filter_proxy_model.setSourceModel(self.icon_list_model)

        self.icon_list_view = IconListView()
        self.icon_list_view.setModel(self.filter_proxy_model)
        self.icon_list_view.itemDoubleClicked.connect(self.accept)
        self.icon_list_view.viewport().installEventFilter(self)
        main_layout.addWidget(self.icon_list_view)

        # Filter
        self.filter_field = FilterField()
        self.filter_field.textChanged.connect(self.filter_proxy_model.setPattern)
        top_layout.addWidget(self.filter_field)

        # Scale
        self.slider = Slider(Qt.Horizontal)
        self.slider.setFixedWidth(120)
        self.slider.setDefaultValue(64)
        self.slider.setRange(48, 128)
        self.setIconSize(64)
        self.slider.valueChanged.connect(self.setIconSize)
        top_layout.addWidget(self.slider)

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

    def setIconSize(self, size):
        size = min(max(size, 48), 128)
        self.slider.setToolTip('Size: ' + str(size))
        self.slider.setValue(size)
        self.icon_list_model.setIconSize(size)
        self.icon_list_view.setIconSize(QSize(size, size))

    def zoomIn(self, amount=4):
        self.setIconSize(self.icon_list_model.iconSize() + amount)

    def zoomOut(self, amount=4):
        self.setIconSize(self.icon_list_model.iconSize() - amount)

    def eventFilter(self, watched, event):
        if watched == self.icon_list_view.viewport() and event.type() == QEvent.Wheel:
            if event.modifiers() == Qt.ControlModifier:
                if event.delta() > 0:
                    self.zoomIn()
                else:
                    self.zoomOut()
                return True
        return False

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Find) or event.key() == Qt.Key_F3:
            self.filter_field.setFocus()
            self.filter_field.selectAll()
        elif event.matches(QKeySequence.ZoomIn):
            self.zoomIn()
        elif event.matches(QKeySequence.ZoomOut):
            self.zoomOut()
        else:
            super(IconListDialog, self).keyPressEvent(event)

    def enableDialogMode(self):
        self.icon_list_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.icon_list_view.enableDoubleClickedSignal()
        self.ok_button.setVisible(True)
        self.cancel_button.setVisible(True)

    @classmethod
    def getIconName(cls, parent=hou.qt.mainWindow(), title='Icons', name=None):
        window = IconListDialog(parent)
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
    window = IconListDialog(hou.qt.mainWindow())
    window.show()
