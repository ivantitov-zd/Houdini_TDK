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
    from PyQt5.QtWidgets import QLineEdit
    from PyQt5.QtGui import QKeySequence
    from PyQt5.QtCore import Qt, pyqtSignal as Signal
except ImportError:
    from PySide2.QtWidgets import QLineEdit
    from PySide2.QtGui import QKeySequence
    from PySide2.QtCore import Qt, Signal


class InputField(QLineEdit):
    # Signals
    accepted = Signal(str)

    def keyPressEvent(self, event):
        key = event.key()
        if event.matches(QKeySequence.Cancel):
            self.clear()
        elif key == Qt.Key_Enter or key == Qt.Key_Return:
            self.accepted.emit(self.text())
        else:
            super(InputField, self).keyPressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton and event.modifiers() == Qt.ControlModifier:
            self.clear()
        else:
            super(InputField, self).mouseReleaseEvent(event)
