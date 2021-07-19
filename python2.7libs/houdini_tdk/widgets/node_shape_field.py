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
    from PyQt5.QtCore import QEvent
    from PyQt5.QtGui import Qt
    from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
except ImportError:
    from PySide2.QtCore import QEvent
    from PySide2.QtGui import Qt
    from PySide2.QtWidgets import QWidget, QHBoxLayout, QPushButton

import hou

from ..node_shapes import NodeShapeListWindow, NodeShapePreview, NodeShape
from .input_field import InputField


class NodeShapeField(QWidget):
    def __init__(self, default_shape=None, initial_shape=None):
        super(NodeShapeField, self).__init__()

        self._default_shape = default_shape
        initial_shape = initial_shape or default_shape

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.text_field = InputField()
        self.text_field.installEventFilter(self)
        layout.addWidget(self.text_field)

        self.shape_preview = NodeShapePreview()
        self.shape_preview.setToolTip('Shape preview')
        self.shape_preview.setFixedSize(52, 24)
        layout.addWidget(self.shape_preview)
        self.text_field.textChanged.connect(self.shape_preview.setShape)

        self.pick_shape_button = QPushButton()
        self.pick_shape_button.setToolTip('Pick shape')
        self.pick_shape_button.setFixedSize(24, 24)
        self.pick_shape_button.setIcon(hou.qt.Icon('NETVIEW_shape_palette', 16, 16))
        self.pick_shape_button.clicked.connect(self.pickShape)
        layout.addWidget(self.pick_shape_button)

        if initial_shape:
            self.text_field.setText(initial_shape)

    def eventFilter(self, watched, event):
        if watched == self.text_field:
            if event.type() == QEvent.MouseButtonPress:
                button = event.button()
                modifiers = event.modifiers()
                if button == Qt.LeftButton and modifiers == Qt.NoModifier:
                    self.text_field.selectAll()
                    return True
        return False

    def text(self):
        return self.text_field.text()

    def setText(self, text):
        self.text_field.setText(text)

    def shape(self):
        name = self.text_field.text()
        if NodeShape.isValidShape(name):
            return name

    def setShape(self, name):
        if name is None:
            self.text_field.setText('')

        if not name:
            return

        if NodeShape.isValidShape(name):
            self.text_field.setText(name)

    def pickShape(self):
        shape_name = NodeShapeListWindow.getShapeName(self, 'Pick Node Shape', self.text_field.text())
        self.setShape(shape_name)
