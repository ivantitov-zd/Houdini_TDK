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
from ..widgets import InputField
from .model import NodeShapeListModel
from .view import NodeShapeListView
from .delegate import NodeShapeDelegate


class NodeShapeListWindow(QDialog):
    def __init__(self, parent=None):
        super(NodeShapeListWindow, self).__init__(parent, Qt.Window)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.setWindowTitle('TDK: Node Shapes')
        self.setWindowIcon(hou.qt.Icon('NETVIEW_shape_palette', 32, 32))
        self.resize(820, 500)

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        # Filter
        self._search_field = InputField()
        self._search_field.setPlaceholderText('Search...')
        main_layout.addWidget(self._search_field)

        # Node Shape List
        self._shape_list_model = NodeShapeListModel(self)
        self._shape_list_model.updateNodeShapeList()

        self._filter_proxy_model = FuzzyProxyModel(self, Qt.DisplayRole)
        self._filter_proxy_model.setSourceModel(self._shape_list_model)
        self._search_field.textChanged.connect(self._filter_proxy_model.setPattern)

        self._shape_list_view = NodeShapeListView()
        self._shape_list_view.setModel(self._filter_proxy_model)
        self._shape_list_view.setItemDelegate(NodeShapeDelegate(self._shape_list_view))
        self._shape_list_view.itemDoubleClicked.connect(self.accept)
        main_layout.addWidget(self._shape_list_view)

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

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Find) or event.key() == Qt.Key_F3:
            self._search_field.setFocus()
            self._search_field.selectAll()
        else:
            super(NodeShapeListWindow, self).keyPressEvent(event)

    def enableDialogMode(self):
        self._shape_list_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self._shape_list_view.enableDoubleClickedSignal()
        self._ok_button.setVisible(True)
        self._cancel_button.setVisible(True)

    @classmethod
    def getShapeName(cls, parent=hou.qt.mainWindow(), title='Node Shapes', name=None):
        window = NodeShapeListWindow(parent)
        window.setWindowTitle('TDK: ' + title)
        window.enableDialogMode()

        if name:
            model = window._shape_list_view.model()
            for row in range(model.rowCount()):
                index = model.index(row, 0)
                if index.data(NodeShapeListModel.ShapeNameRole) == name:
                    window._shape_list_view.setCurrentIndex(index)
                    break

        if window.exec_() and window._shape_list_view.currentIndex().isValid():
            return window._shape_list_view.currentIndex().data(NodeShapeListModel.ShapeNameRole)


def findNodeShape(**kwargs):
    window = NodeShapeListWindow(hou.qt.mainWindow())
    window.show()
