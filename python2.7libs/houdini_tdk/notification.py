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
    from PyQt5.QtCore import QTimer, QMetaMethod
except ImportError:
    from PySide2.QtCore import QTimer, QMetaMethod

import hou

timer = QTimer(hou.qt.mainWindow())
timer.setSingleShot(True)


def _removeNotification(target_message, target_severity):
    """ Works in Houdini 18.0.472+ only. """
    try:
        current_message, _ = hou.ui.statusMessage()
    except AttributeError:
        return

    if target_severity == hou.severityType.Error:
        target_message = 'Error:       ' + target_message
    elif target_severity == hou.severityType.Warning:
        target_message = 'Warning:     ' + target_message
    elif target_severity == hou.severityType.Fatal:
        target_message = 'Fatal error: ' + target_message

    if current_message == target_message:
        hou.ui.setStatusMessage('')


def notify(message, severity_type=hou.severityType.ImportantMessage, duration=2.5):
    hou.ui.setStatusMessage(message, severity_type)

    try:
        timer.timeout.disconnect()
    except RuntimeError:
        pass
    timer.timeout.connect(lambda: _removeNotification(message, severity_type))
    timer.start(int(duration * 1000))
