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

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

    Signal = pyqtSignal
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *


def fuzzyMatch(pattern, text):
    if pattern == text:
        return True

    index = 0
    try:
        for char in text:
            if char == pattern[index]:
                index += 1
    except IndexError:
        pass

    if index < len(pattern):
        return False

    return True


def fuzzyMatchScore(pattern, text):
    if pattern == text:
        return 999999

    weight = 0
    count = 0
    index = 0
    try:
        for char in text:
            if char == pattern[index]:
                count += 1
                index += 1
            elif count != 0:
                weight += count * count
                count = 0
    except IndexError:
        pass

    weight += count * count
    if index < len(pattern):
        return weight

    return weight + (1 - text.index(pattern[0]) / 500.0)


class FuzzyProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None, accept_text_role=Qt.UserRole, comp_text_role=Qt.DisplayRole):
        super(FuzzyProxyModel, self).__init__(parent)

        self.setFilterCaseSensitivity(Qt.CaseInsensitive)

        self._accept_text_role = accept_text_role
        self.comp_text_role = comp_text_role

        self._pattern = ''

    def setPattern(self, pattern):
        self._pattern = pattern.lower()
        self.invalidate()

    def filterAcceptsRow(self, source_row, source_parent):
        if not self._pattern:
            return True

        source_model = self.sourceModel()
        current_index = source_model.index(source_row, 0, source_parent)
        text = current_index.data(self._accept_text_role)
        matches = fuzzyMatch(self._pattern, text.lower())

        if not matches and source_model.hasChildren(current_index):
            for row in range(source_model.rowCount(current_index)):
                if super(FuzzyProxyModel, self).filterAcceptsRow(row, current_index):
                    return True

        return matches

    def lessThan(self, source_left, source_right):
        if not self._pattern:
            return source_left.row() < source_right.row()

        text1 = source_left.data(self.comp_text_role)
        text2 = source_right.data(self.comp_text_role)

        if self.sortCaseSensitivity() == Qt.CaseInsensitive:
            text1 = text1.lower()
            text2 = text2.lower()

        weight1 = fuzzyMatchScore(self._pattern, text1)
        weight2 = fuzzyMatchScore(self._pattern, text2)

        return weight1 < weight2
