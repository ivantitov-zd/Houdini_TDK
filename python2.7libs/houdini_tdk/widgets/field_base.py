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
    from PyQt5.QtWidgets import QHBoxLayout, QWidget, QLabel
    from PyQt5.QtCore import Qt
except ImportError:
    from PySide2.QtWidgets import QHBoxLayout, QWidget, QLabel
    from PySide2.QtCore import Qt


class FieldBase(QWidget):
    def __init__(self, label_text=None, label_width=None, label_alignment=Qt.AlignLeft | Qt.AlignVCenter):
        super(FieldBase, self).__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        if label_text is not None:
            self.label = QLabel(label_text)

            if label_width is not None:
                self.label.setFixedWidth(label_width)

            self.label.setAlignment(label_alignment)
            layout.addWidget(self.label)
