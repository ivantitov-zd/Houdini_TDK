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

from .delegate import OperatorManagerLibraryDelegate

ICON_SIZE = 16


class OperatorManagerView(QTreeView):
    def __init__(self):
        super(OperatorManagerView, self).__init__()

        header = self.header()
        header.setSectionsMovable(False)
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.hide()

        self.setUniformRowHeights(True)
        self.setIconSize(QSize(16, 16))

        self.setItemDelegate(OperatorManagerLibraryDelegate())
        # self.setAlternatingRowColors(True)  # Disabled due to a bug that clipping delegate's text

        self.__createActions()
        self.__createContextMenus()

    def __createActions(self):
        self._open_location_action = QAction(hou.qt.Icon('BUTTONS_folder', ICON_SIZE, ICON_SIZE), 'Open location')

        self._install_library_action = QAction('Install')

        self._uninstall_library_action = QAction('Uninstall')

        self._reinstall_library_action = QAction(hou.qt.Icon('MISC_loading', ICON_SIZE, ICON_SIZE), 'Reinstall')

        self._merge_with_library_action = QAction('Merge with Library')

        self._pack_action = QAction(hou.qt.Icon('DESKTOP_otl', ICON_SIZE, ICON_SIZE), 'Pack')

        self._unpack_action = QAction(hou.qt.Icon('DESKTOP_expanded_otl', ICON_SIZE, ICON_SIZE), 'Unpack')

        self._backup_list_action = QAction(hou.qt.Icon('BUTTONS_history', ICON_SIZE, ICON_SIZE), 'Backups...')

        self._open_type_properties_action = QAction(hou.qt.Icon('BUTTONS_gear_mini', ICON_SIZE, ICON_SIZE),
                                                    'Open type properties...')

        self._change_instances_to_action = QAction('Change instances to...')

        self._run_hda_doctor_action = QAction(hou.qt.Icon('SOP_polydoctor', ICON_SIZE, ICON_SIZE), 'Run HDA Doctor...')

        self._find_usages_action = QAction(hou.qt.Icon('BUTTONS_search', ICON_SIZE, ICON_SIZE), 'Find usages...')

        self._find_dependencies_action = QAction(hou.qt.Icon('PANETYPES_network', ICON_SIZE, ICON_SIZE),
                                                 'Find dependencies...')

        self._show_statistics_action = QAction(hou.qt.Icon('BUTTONS_info', ICON_SIZE, ICON_SIZE), 'Show statistics...')

        self._create_instance_action = QAction('Instance')

        self._create_new_hda_action = QAction(hou.qt.Icon('SOP_compile_begin', ICON_SIZE, ICON_SIZE),
                                              'New HDA...')

        self._create_new_version_action = QAction(hou.qt.Icon('BUTTONS_multi_insertbefore', ICON_SIZE, ICON_SIZE),
                                                  'New version...')

        self._create_black_box_action = QAction(hou.qt.Icon('NETVIEW_hda_locked_badge', ICON_SIZE, ICON_SIZE),
                                                'Black box...')

        self._copy_action = QAction(hou.qt.Icon('BUTTONS_copy', ICON_SIZE, ICON_SIZE), 'Copy...')

        self._move_action = QAction(hou.qt.Icon('BUTTONS_move_to_right', ICON_SIZE, ICON_SIZE), 'Move...')

        self._rename_action = QAction(hou.qt.Icon('MISC_rename', ICON_SIZE, ICON_SIZE), 'Rename...')

        self._add_alias_action = QAction(hou.qt.Icon('BUTTONS_tag', ICON_SIZE, ICON_SIZE), 'Add alias...')

        self._delete_action = QAction(hou.qt.Icon('BUTTONS_delete', ICON_SIZE, ICON_SIZE), 'Delete')

        self._hide_action = QAction(hou.qt.Icon('BUTTONS_close', ICON_SIZE, ICON_SIZE), 'Hide')

        self._deprecate_action = QAction(hou.qt.Icon('BUTTONS_do_not', ICON_SIZE, ICON_SIZE), 'Deprecate')

        self._compare_action = QAction(hou.qt.Icon('BUTTONS_restore', ICON_SIZE, ICON_SIZE), 'Compare...')

    def __createContextMenus(self):
        self._library_menu = QMenu(self)

        self._library_menu.addAction(self._open_location_action)
        self._library_menu.addSeparator()
        self._library_menu.addAction(self._install_library_action)
        self._library_menu.addAction(self._uninstall_library_action)
        self._library_menu.addAction(self._reinstall_library_action)
        self._library_menu.addSeparator()
        self._library_menu.addAction(self._merge_with_library_action)
        self._library_menu.addAction(self._pack_action)
        self._library_menu.addAction(self._unpack_action)
        self._library_menu.addSeparator()
        self._library_menu.addAction(self._backup_list_action)

        self._definition_menu = QMenu(self)

        self._definition_menu.addAction(self._open_type_properties_action)
        self._definition_menu.addAction(self._change_instances_to_action)

        self._definition_inspect_menu = QMenu('Inspect', self)
        self._definition_menu.addMenu(self._definition_inspect_menu)

        self._definition_inspect_menu.addAction(self._run_hda_doctor_action)
        self._definition_inspect_menu.addAction(self._find_usages_action)
        self._definition_inspect_menu.addAction(self._find_dependencies_action)
        self._definition_inspect_menu.addAction(self._show_statistics_action)

        self._definition_create_menu = QMenu('Create', self)
        self._definition_menu.addMenu(self._definition_create_menu)

        self._definition_create_menu.addAction(self._create_instance_action)
        self._definition_create_menu.addAction(self._create_new_hda_action)
        self._definition_create_menu.addAction(self._create_new_version_action)
        self._definition_create_menu.addAction(self._create_black_box_action)

        self._definition_edit_menu = QMenu('Edit', self)
        self._definition_menu.addMenu(self._definition_edit_menu)

        self._definition_edit_menu.addAction(self._copy_action)
        self._definition_edit_menu.addSeparator()
        self._definition_edit_menu.addAction(self._move_action)
        self._definition_edit_menu.addAction(self._rename_action)
        self._definition_edit_menu.addAction(self._add_alias_action)
        self._definition_edit_menu.addSeparator()
        self._definition_edit_menu.addAction(self._delete_action)
        self._definition_edit_menu.addAction(self._hide_action)
        self._definition_edit_menu.addAction(self._deprecate_action)

        self._definition_menu.addAction(self._compare_action)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

    def showContextMenu(self):
        index = self.currentIndex()

        if not index.isValid():
            return

        if isinstance(index.data(Qt.UserRole), basestring):
            self._library_menu.exec_(QCursor.pos())
        else:
            icon = index.model().index(index.row(), 0, index.parent()).data(Qt.DecorationRole)
            self._create_instance_action.setIcon(icon)
            self._definition_menu.exec_(QCursor.pos())
