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


def isRevertToDefaultEvent(event):
    return event.modifiers() == Qt.ControlModifier and event.button() == Qt.MiddleButton


class Slider(QSlider):
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super(Slider, self).__init__(orientation, parent)
        self._default_value = 0
        self._value_ladder_active = False

    def revertToDefault(self):
        self.setValue(self._default_value)

    def setDefaultValue(self, value):
        self._default_value = value

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:  # Todo: Revert to default
            hou.ui.openValueLadder(self.value(), self.setValue,
                                   data_type=hou.valueLadderDataType.Int)
            self._value_ladder_active = True
        elif event.button() == Qt.LeftButton:
            event = QMouseEvent(QEvent.MouseButtonPress, event.pos(),
                                Qt.MiddleButton, Qt.MiddleButton, Qt.NoModifier)
        super(Slider, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._value_ladder_active:
            hou.ui.updateValueLadder(event.globalX(), event.globalY(),
                                     bool(event.modifiers() & Qt.AltModifier),
                                     bool(event.modifiers() & Qt.ShiftModifier))
        else:
            super(Slider, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._value_ladder_active and event.button() == Qt.MiddleButton:
            hou.ui.closeValueLadder()
            self._value_ladder_active = False
        elif isRevertToDefaultEvent(event):
            self.revertToDefault()
        else:
            super(Slider, self).mouseReleaseEvent(event)
