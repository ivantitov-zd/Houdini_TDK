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

import hou


class CounterGroup(object):
    __slots__ = 'name', 'parent', 'children', '_predicate'

    def __init__(self, name, parent=None, predicate=lambda item: True):
        self.name = name
        self.parent = parent
        if parent:
            parent.children.append(self)
        self._predicate = predicate
        self.children = []

    def count(self, item):
        if self._predicate(item):
            for child in self.children:
                child.count(item)

    def __repr__(self):
        return 'CounterGroup({}, {})'.format(self.name, self.parent)


class Counter(object):
    __slots__ = 'name', 'parent', '_predicate', 'value', '_converter'

    def __init__(self, name, parent, predicate=lambda item: True, converter=lambda i, v: v + 1):
        self.name = name
        self.parent = parent
        if parent:
            parent.children.append(self)
        self._predicate = predicate
        self._converter = converter
        self.value = 0

    def count(self, item):
        if self._predicate(item):
            self.value = self._converter(item, self.value)

    def __repr__(self):
        return 'Counter({}, {})'.format(self.name, self.parent)


def parmHasExpression(parm):
    try:
        parm.expression()
        return True
    except hou.OperationFailed:
        return False


def parmHasCode(parm):
    parm_template = parm.parmTemplate()
    if not isinstance(parm_template, hou.StringParmTemplate):
        return False

    if parmHasExpression(parm):
        return True

    tags = parm_template.tags()
    if tags.get('editor') == '1':
        return True

    return False


def allSubItems(root_node, include_parms=False):
    if not root_node:
        return

    try:
        for item in root_node.allItems():
            yield item
            if include_parms:
                for parm in item.parms():
                    yield parm
            for sub_item in allSubItems(item):
                yield sub_item
    except hou.OperationFailed:  # Item is not a network
        return
    except AttributeError:  # Item is not a hou.Node instance
        return
    except RecursionError:
        print('Black hole detected!')
        raise


def gatherNetworkStats(root_node):
    current_update_mode = hou.updateModeSetting()
    hou.setUpdateMode(hou.updateMode.Manual)

    root_depth = root_node.path().count('/')

    stats = []

    nodes_group = CounterGroup('Nodes', predicate=lambda i: isinstance(i, hou.Node))
    stats.append(nodes_group)
    Counter('Total', nodes_group)
    Counter('Subnetworks', nodes_group, predicate=lambda i: i.isNetwork())  # Fixme
    Counter('Inside Locked', nodes_group, predicate=lambda i: not i.isEditable())
    Counter('Maximum Depth', nodes_group, converter=lambda i, v: max(i.path().count('/') - root_depth, v))

    parms_group = CounterGroup('Parameters', predicate=lambda i: isinstance(i, hou.Parm))
    stats.append(parms_group)
    Counter('Animated', parent=parms_group, predicate=lambda i: len(i.keyframes()) > 1)
    parms_links_group = CounterGroup('Links to', parms_group)
    Counter('Parameters', parms_links_group, predicate=lambda i: i.getReferencedParm() != i)
    Counter('Nodes', parms_links_group)
    Counter('Folders', parms_links_group)
    Counter('Files', parms_links_group)
    Counter('Web', parms_links_group)

    code_group = CounterGroup('Code', predicate=lambda i: isinstance(i, hou.Parm) and parmHasCode(i))
    stats.append(code_group)
    code_python_group = CounterGroup('Python', code_group)
    Counter('Total', code_python_group)
    Counter('Lines', code_python_group)
    Counter('Empty', code_python_group)
    Counter('Comments', code_python_group)
    code_hscript_group = CounterGroup('HScript', code_group)
    Counter('Total', code_hscript_group)
    Counter('Lines', code_hscript_group)
    Counter('Empty', code_hscript_group)
    Counter('Comments', code_hscript_group)
    code_vex_group = CounterGroup('VEX', code_group)
    Counter('Total', code_vex_group)
    Counter('Lines', code_vex_group)
    Counter('Empty', code_vex_group)
    Counter('Comments', code_vex_group)
    code_opencl_group = CounterGroup('OpenCL', code_group)
    Counter('Total', code_opencl_group)
    Counter('Lines', code_opencl_group)
    Counter('Empty', code_opencl_group)
    Counter('Comments', code_opencl_group)

    for item in allSubItems(root_node, include_parms=True):
        for stat in stats:
            stat.count(item)

    hou.setUpdateMode(current_update_mode)
    return tuple(stats)
