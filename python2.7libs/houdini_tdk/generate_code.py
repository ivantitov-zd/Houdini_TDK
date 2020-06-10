"""
Tool Development Kit for SideFX Houdini
Copyright (C) 2020  Ivan Titov

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

import os
import tempfile

import hou

from notification import notify


def generateCode(**kwargs):
    if 'node' in kwargs:
        nodes = kwargs['node'],
    else:
        nodes = hou.selectedNodes()
    if not nodes:
        notify('No node selected', hou.severityType.Error)
        return
    code = ''.join(node.asCode(brief=True) for node in nodes)
    if kwargs['ctrlclick'] or kwargs['shiftclick']:
        path = tempfile.mktemp('.py')
        with open(path, 'w') as file:
            file.write(code)
        if len(nodes) == 1:
            title = nodes[0].path()
        else:
            title = os.path.dirname(nodes[0].path())
        if kwargs['ctrlclick']:
            hou.ui.openFileEditor(title, path)
        else:
            os.startfile(path)
    else:
        hou.ui.copyTextToClipboard(code)
        notify('Code was generated and copied')
