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

import os

import hou


def parmHasExpression(parm):
    try:
        parm.expression()
        return True
    except hou.OperationFailed:
        return False


def parmHasCode(parm):
    pass


def gatherNetworkStats(root_node):
    data = {
        'nodes': {
            'total': 0,
            'subnetworks': 0,
            'inside_locked': 0,
            'max_depth': 0
        },
        'parms': {
            'animated': 0,
            'links_to': {
                'parms': 0,
                'nodes': 0,
                'folders': 0,
                'files': 0,
                'web': 0
            }
        },
        'code': {
            'python': {
                'total': 0,
                'lines': 0,
                'empty': 0,
                'comments': 0
            },
            'hscript': {
                'total': 0,
                'lines': 0,
                'empty': 0,
                'comments': 0
            },
            'vex': {
                'total': 0,
                'lines': 0,
                'empty': 0,
                'comments': 0
            },
            'opencl': {
                'total': 0,
                'lines': 0,
                'empty': 0,
                'comments': 0
            }
        }
    }

    current_update_mode = hou.updateModeSetting()
    hou.setUpdateMode(hou.updateMode.Manual)

    for node in root_node.allSubChildren():
        data['nodes']['total'] += 1

        if node.isNetwork():
            data['nodes']['subnetworks'] += 1

        if not node.isEditable():
            data['nodes']['inside_locked'] += 1

        depth = node.path().count('/') - 1
        max_depth = data['nodes']['max_depth']
        data['nodes']['max_depth'] = max(depth, max_depth)

        for parm in node.parms():
            if parm.getReferencedParm() != parm:
                data['parms']['links_to']['parms'] += 1

            parm_template = parm.parmTemplate()
            if isinstance(parm_template, hou.StringParmTemplate):
                string_type = parm_template.stringType()
                path = parm.evalAsString()
                if string_type == hou.stringParmType.NodeReference:
                    try:
                        if parm.evalAsNode() is not None:
                            data['parms']['links_to']['nodes'] += 1
                    except hou.TypeError:
                        pass
                elif string_type == hou.stringParmType.NodeReferenceList:
                    data['parms']['links_to']['nodes'] += len(parm.evalAsNodes())
                elif string_type == hou.stringParmType.FileReference:
                    if os.path.exists(path):
                        if os.path.isdir(path):
                            data['parms']['links_to']['folders'] += 1
                        else:  # os.path.isfile(path)
                            data['parms']['links_to']['files'] += 1
                elif path.startswith('http'):
                    data['parms']['links_to']['web'] += 1

                if parmHasExpression(parm):
                    lang = {
                        hou.exprLanguage.Python: 'python',
                        hou.exprLanguage.Hscript: 'hscript'
                    }[parm.expressionLanguage()]
                    expr = parm.expression()
                    data['code'][lang]['total'] += 1
                    data['code'][lang]['lines'] += expr.count('\n')
                    data['code'][lang]['empty'] += expr.count('\n\n')
                    for line in expr.split('\n'):
                        line = line.lstrip()
                        if lang == 'python' and line.startswith('#'):
                            data['code'][lang]['comments'] += 1
                        elif line.startswith('//'):
                            data['code'][lang]['comments'] += 1

            if len(parm.keyframes()) > 1:
                data['parms']['animated'] += 1

    hou.setUpdateMode(current_update_mode)

    return data
