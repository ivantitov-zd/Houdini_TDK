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

from .filter_field import FilterField
from .node_shape_list_model import NodeShapeListModel
from .node_shape_list_view import NodeShapeListView
from .node_shape_delegate import NodeShapeDelegate
from .fuzzy_filter_proxy_model import FuzzyFilterProxyModel


class NodeShapeListDialog(QDialog):
    def __init__(self, parent=None):
        super(NodeShapeListDialog, self).__init__(parent, Qt.Window)

        self.setWindowTitle('TDK: Node Shapes')
        self.setWindowIcon(hou.qt.Icon('NETVIEW_shape_palette', 32, 32))
        self.resize(820, 500)

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        # Filter
        self.filter_field = FilterField()
        main_layout.addWidget(self.filter_field)

        # Node Shape List
        self.shape_list_model = NodeShapeListModel(self)
        self.shape_list_model.updateNodeShapeList()

        self.filter_proxy_model = FuzzyFilterProxyModel(self, Qt.DisplayRole)
        self.filter_proxy_model.setSourceModel(self.shape_list_model)
        self.filter_field.textChanged.connect(self.filter_proxy_model.setFilterPattern)

        self.shape_list_view = NodeShapeListView()
        self.shape_list_view.setModel(self.filter_proxy_model)
        self.shape_list_view.setItemDelegate(NodeShapeDelegate(self.shape_list_view))
        self.shape_list_view.itemDoubleClicked.connect(self.accept)
        main_layout.addWidget(self.shape_list_view)

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
            super(NodeShapeListDialog, self).keyPressEvent(event)

    def enableDialogMode(self):
        self.shape_list_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.shape_list_view.enableDoubleClickedSignal()
        self.ok_button.setVisible(True)
        self.cancel_button.setVisible(True)

    @classmethod
    def getShapeName(cls, parent=hou.qt.mainWindow(), title='Node Shapes', name=None):
        window = NodeShapeListDialog(parent)
        window.setWindowTitle('TDK: ' + title)
        window.enableDialogMode()

        if name:
            model = window.shape_list_view.model()
            for row in range(model.rowCount()):
                index = model.index(row, 0)
                if index.data(NodeShapeListModel.ShapeNameRole) == name:
                    window.shape_list_view.setCurrentIndex(index)
                    break

        if window.exec_() and window.shape_list_view.currentIndex().isValid():
            return window.shape_list_view.currentIndex().data(NodeShapeListModel.ShapeNameRole)


def findNodeShape(**kwargs):
    window = NodeShapeListDialog(hou.qt.mainWindow())
    window.show()
