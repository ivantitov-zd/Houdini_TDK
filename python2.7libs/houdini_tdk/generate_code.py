# coding: utf-8

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

import os
import tempfile

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

from notification import notify


def _openCode(code, node, in_houdini):
    path = tempfile.mktemp('.py')
    with open(path, 'w') as file:
        file.write(code)

    if in_houdini:
        hou.ui.openFileEditor(node.path(), path)
        notify('Code was generated and opened in internal editor')
    else:
        os.startfile(path)
        notify('Code was generated and opened in external editor')


def _copyCode(code):
    hou.ui.copyTextToClipboard(code)
    notify('Code was generated and copied')


class ActionType:
    Internal = 1
    External = 2
    Copy = 4

    @staticmethod
    def byKWARGS(**kwargs):
        return kwargs['ctrlclick'] * ActionType.Internal + \
               kwargs['shiftclick'] * ActionType.External \
               + kwargs['altclick'] * ActionType.Copy


def generateCode(action_type, node=None, options=None):
    nodes = (node,) if node else hou.selectedNodes()

    if not nodes:
        notify('No node selected', hou.severityType.Error)
        return

    if not options:
        options = {'brief': True}

    code = ''.join(node.asCode(**options) for node in nodes)

    if action_type & (ActionType.Internal | ActionType.External):
        _openCode(code, nodes[0], action_type & ActionType.Internal)
    else:
        _copyCode(code)


class GenerateCodeSettings(QDialog):
    def __init__(self, node, parent=None):
        super(GenerateCodeSettings, self).__init__(parent)

        # Data
        self._node = node

        # UI
        self.setWindowTitle('Generate Code: Settings')
        self.setWindowIcon(hou.qt.Icon('MISC_python', 32, 32))
        self.resize(400, 200)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        self.brief_toggle = QCheckBox('Brief')
        self.brief_toggle.setToolTip('Do not set values if they are the parameter’s default. '
                                     'Applies to the contents of the node if either recurse '
                                     'or save_box_contents is True.')
        self.brief_toggle.setChecked(True)
        main_layout.addWidget(self.brief_toggle)

        self.recurse_toggle = QCheckBox('Recurse')
        self.recurse_toggle.setToolTip('Recursively apply to the entire operator hierarchy.')
        self.recurse_toggle.setChecked(False)
        main_layout.addWidget(self.recurse_toggle)

        self.save_box_contents_toggle = QCheckBox('Save box contents')
        self.save_box_contents_toggle.setToolTip('Script the contents of the node.')
        self.save_box_contents_toggle.setChecked(False)
        main_layout.addWidget(self.save_box_contents_toggle)

        self.save_channels_only_toggle = QCheckBox('Save channels only')
        self.save_channels_only_toggle.setToolTip('Only output channels. '
                                                  'Applies to the contents of the node '
                                                  'if either recurse or save_box_contents is True.')
        self.save_channels_only_toggle.setChecked(True)
        main_layout.addWidget(self.save_channels_only_toggle)

        self.save_creation_commands_toggle = QCheckBox('Save creation commands')
        self.save_creation_commands_toggle.setToolTip('Generate a creation script for the node. '
                                                      'If set to False, the generated script assumes '
                                                      'that the network box already exists. When set '
                                                      'to True, the script will begin by creating the '
                                                      'network box.')
        self.save_creation_commands_toggle.setChecked(True)
        main_layout.addWidget(self.save_creation_commands_toggle)

        self.save_keys_in_frames_toggle = QCheckBox('Save keys in frames')
        self.save_keys_in_frames_toggle.setToolTip('Output channel and key times in samples (frames) '
                                                   'instead of seconds. Applies to the contents of the '
                                                   'node if either recurse or save_box_contents is True.')
        self.save_keys_in_frames_toggle.setChecked(False)
        main_layout.addWidget(self.save_keys_in_frames_toggle)

        self.save_outgoing_wires_toggle = QCheckBox('Save outgoing wires')
        self.save_outgoing_wires_toggle.setChecked(False)
        main_layout.addWidget(self.save_outgoing_wires_toggle)

        self.save_parm_values_only_toggle = QCheckBox('Save parm values only')
        self.save_parm_values_only_toggle.setToolTip('Evaluate parameters, saving their values '
                                                     'instead of the expressions. Applies to the contents '
                                                     'of the node if either recurse or save_box_contents '
                                                     'is True.')
        self.save_parm_values_only_toggle.setChecked(False)
        main_layout.addWidget(self.save_parm_values_only_toggle)

        self.save_spare_parms_toggle = QCheckBox('Save spare parms')
        self.save_spare_parms_toggle.setToolTip('Save spare parameters as well. When save_creation_commands '
                                                'is True, commands for creating spare parameters will also '
                                                'be output. Applies to the contents of the node if either '
                                                'recurse or save_box_contents is True.')
        self.save_spare_parms_toggle.setChecked(True)
        main_layout.addWidget(self.save_spare_parms_toggle)

        self.function_name_field = QLineEdit()
        self.function_name_field.setPlaceholderText('Function name')
        self.function_name_field.setToolTip('If a function_name is specified, the output will be wrapped '
                                            'in a Python function.')
        main_layout.addWidget(self.function_name_field)

        main_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding))

        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(4)
        main_layout.addLayout(action_layout)

        action_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored))

        generate_label = QLabel('Generate and ')
        action_layout.addWidget(generate_label)

        self.show_button = QPushButton('Show')
        self.show_button.setToolTip('Open in internal Houdini editor')
        self.show_button.clicked.connect(self.onShowClicked)
        action_layout.addWidget(self.show_button)

        self.open_button = QPushButton('Open')
        self.show_button.setToolTip('Open in external editor')
        self.open_button.clicked.connect(self.onOpenClicked)
        action_layout.addWidget(self.open_button)

        self.copy_button = QPushButton('Copy')
        self.copy_button.setToolTip('Copy to the system clipboard')
        self.copy_button.clicked.connect(self.onCopyClicked)
        action_layout.addWidget(self.copy_button)

    def options(self):
        return {
            'brief': self.brief_toggle.isChecked(),
            'recurse': self.recurse_toggle.isChecked(),
            'save_channels_only': self.save_channels_only_toggle.isChecked(),
            'save_creation_commands': self.save_creation_commands_toggle.isChecked(),
            'save_keys_in_frames': self.save_keys_in_frames_toggle.isChecked(),
            'save_outgoing_wires': self.save_outgoing_wires_toggle.isChecked(),
            'save_parm_values_only': self.save_parm_values_only_toggle.isChecked(),
            'save_spare_parms': self.save_spare_parms_toggle.isChecked(),
            'function_name': self.function_name_field.text()  # Todo: validate
        }

    def onShowClicked(self):
        generateCode(ActionType.Internal, self._node, self.options())
        self.accept()

    def onOpenClicked(self):
        generateCode(ActionType.External, self._node, self.options())
        self.accept()

    def onCopyClicked(self):
        generateCode(ActionType.Copy, self._node, self.options())
        self.accept()


def showGenerateCode(**kwargs):
    if kwargs['altclick']:
        window = GenerateCodeSettings(kwargs.get('node'), hou.qt.mainWindow())
        window.show()
    else:
        generateCode(ActionType.byKWARGS(**kwargs), kwargs.get('node'))
