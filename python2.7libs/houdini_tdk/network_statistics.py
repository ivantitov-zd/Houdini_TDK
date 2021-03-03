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

import os

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


def parmHasExpression(parm):
    try:
        parm.expression()
        return True
    except hou.OperationFailed:
        return False


def parmHasCode(parm):
    pass


class StatItem:
    def __init__(self, text=None, value=None, child_items=()):
        self.text = text
        self.value = str(value) if value is not None else None
        self._index = None
        self.parent = None
        self._child_items = child_items or ()
        for index, item in enumerate(self._child_items):
            item.index = index
            item.parent = self

    def __getitem__(self, item):
        return self._child_items[item]

    def __len__(self):
        return len(self._child_items)


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


class NetworkStatsModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(NetworkStatsModel, self).__init__(parent)

        self._data = StatItem()

    def updateData(self, node):
        self.beginResetModel()
        data = gatherNetworkStats(node)
        self._data = StatItem(None, None,
                              [
                                  StatItem('Nodes', None,
                                           [
                                               StatItem('Total', data['nodes']['total']),
                                               StatItem('Subnetworks', data['nodes']['subnetworks']),
                                               StatItem('Inside Locked', data['nodes']['inside_locked']),
                                               StatItem('Maximum Depth', data['nodes']['max_depth'])
                                           ]),
                                  StatItem('Parameters', None,
                                           [
                                               StatItem('Animated', data['parms']['animated']),
                                               StatItem('Links to', None,
                                                        [
                                                            StatItem('parameters', data['parms']['links_to']['parms']),
                                                            StatItem('nodes', data['parms']['links_to']['nodes']),
                                                            StatItem('folders', data['parms']['links_to']['folders']),
                                                            StatItem('files', data['parms']['links_to']['files']),
                                                            StatItem('web', data['parms']['links_to']['web'])
                                                        ])
                                           ])
                                  # Todo: code stats section
                              ])
        self.endResetModel()

    def hasChildren(self, parent):
        if not parent.isValid():
            return True

        return bool(parent.internalPointer())

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        item = index.internalPointer()
        if item.text is None:
            return QModelIndex()

        return self.createIndex(item.index, 0, item.parent)

    def columnCount(self, parent):
        return 2

    def rowCount(self, parent):
        if not parent.isValid():
            return len(self._data)

        item = parent.internalPointer()
        return len(item)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            item = self._data[row]
        else:
            item = parent.internalPointer()[row]

        return self.createIndex(row, column, item)

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():
            return

        column = index.column()
        item = index.internalPointer()

        if column == 0:
            if role == Qt.DisplayRole:
                return item.text
        elif column == 1:
            if role == Qt.DisplayRole:
                return item.value
        # Todo: column 3 - percentage


class NetworkStatsView(QTreeView):
    def __init__(self):
        super(NetworkStatsView, self).__init__()

        self.setWindowTitle('TDK: Network Statistics')

        header = self.header()
        header.setSectionsMovable(False)
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.hide()

        self.setUniformRowHeights(True)

        self.setRootIsDecorated(False)
        self.setStyleSheet('QTreeView::branch {border-image: none; image: none;}')
        self.setItemsExpandable(False)

        model = NetworkStatsModel(self)
        self.setModel(model)


class NetworkStatsWindow(QDialog):
    def __init__(self, parent=hou.qt.mainWindow()):
        super(NetworkStatsWindow, self).__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self._stats_view = NetworkStatsView()
        layout.addWidget(self._stats_view)

    def updateData(self, node):
        self._stats_view.model().updateData(node)
        self._stats_view.expandAll()


def showStatsForNode(node, **kwargs):
    hou.session.window = NetworkStatsWindow()
    hou.session.window.setWindowTitle('TDK: Network Statistics: ' + node.path())
    hou.session.window.updateData(node)
    hou.session.window.show()
