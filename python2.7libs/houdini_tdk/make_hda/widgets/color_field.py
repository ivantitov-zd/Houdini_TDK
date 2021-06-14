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
    from PyQt5.QtGui import Qt, QColor
    from PyQt5.QtWidgets import QWidget, QHBoxLayout, QColorDialog
except ImportError:
    from PySide2.QtCore import QEvent
    from PySide2.QtGui import Qt, QColor
    from PySide2.QtWidgets import QWidget, QHBoxLayout, QColorDialog

import hou

from ...widgets import FieldBase, InputField


class ColorField(FieldBase):
    def __init__(self, default_color=None, initial_color=None):
        super(ColorField, self).__init__('Color', 80)

        self._default_color = default_color
        initial_color = initial_color or default_color

        self.text_field = InputField()
        self.text_field.installEventFilter(self)
        self.layout().addWidget(self.text_field)

        self.pick_color_button = hou.qt.ColorSwatchButton()
        self.pick_color_button.disconnect(self.pick_color_button)
        self.pick_color_button.setToolTip('Pick color')
        self.pick_color_button.setFixedSize(52, 24)
        self.pick_color_button.clicked.connect(self.pickColor)
        self.layout().addWidget(self.pick_color_button)
        self.text_field.textChanged.connect(self._onColorNameChanged)

        # Filling
        if initial_color:
            self.text_field.setText(initial_color.name())

    def eventFilter(self, watched, event):
        if watched == self.text_field:
            if event.type() == QEvent.MouseButtonPress:
                button = event.button()
                modifiers = event.modifiers()
                if button == Qt.LeftButton and modifiers == Qt.NoModifier:
                    self.text_field.selectAll()
                    return True
                elif button == Qt.MiddleButton and modifiers == Qt.ControlModifier:
                    self.text_field.setText(self._default_color.name())
                    return True
        return False

    def text(self):
        return self.text_field.text()

    def setText(self, text):
        self.text_field.setText(text)

    def color(self):
        color_name = self.text_field.text()
        if QColor.isValidColor(color_name):
            color = QColor(color_name)
            if color != self._default_color:
                return color

    def setColor(self, color):
        if color is None:
            self.text_field.setText('')

        self.text_field.setText(color.name())

    def _onColorNameChanged(self, name):
        self.pick_color_button.setColor(QColor(name))

    def pickColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self._onColorPicked(color)
            self._onColorNameChanged(color.name())

    def _onColorPicked(self, color):
        self.text_field.blockSignals(True)
        self.text_field.setText(color.name())
        self.text_field.blockSignals(False)
