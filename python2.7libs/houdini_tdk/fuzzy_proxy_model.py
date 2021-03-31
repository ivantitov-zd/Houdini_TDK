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


def fuzzyMatchWeight(pattern, text, cache={}):
    pattern_length = len(pattern)

    if pattern_length <= 2:
        cache_token = pattern + '_' + text
        if cache_token in cache:
            return cache[cache_token]

    if pattern == text:
        weight = pattern_length * pattern_length + 1
    else:
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
        if index >= pattern_length:
            weight = weight + (1 - text.index(pattern[0]) / 1000.0)

    if pattern_length <= 2:
        cache[cache_token] = weight
    return weight


class FuzzyProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None, accept_text_role=Qt.UserRole, comp_text_role=Qt.DisplayRole):
        super(FuzzyProxyModel, self).__init__(parent)

        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setSortCaseSensitivity(Qt.CaseInsensitive)

        self._accept_text_role = accept_text_role
        self._comp_text_role = comp_text_role

        self._pattern = ''
        self._pattern_case_insensitive = ''

    def setPattern(self, pattern):
        self._pattern = pattern
        self._pattern_case_insensitive = pattern.lower()
        self.invalidate()

    def _match(self, index):
        text = index.data(self._accept_text_role)
        if self.filterCaseSensitivity() == Qt.CaseInsensitive:
            matches = fuzzyMatch(self._pattern_case_insensitive, text.lower())
        else:
            matches = fuzzyMatch(self._pattern, text)
        return matches

    def filterAcceptsRow(self, source_row, source_parent):
        if not self._pattern:
            return True

        source_model = self.sourceModel()
        current_index = source_model.index(source_row, 0, source_parent)
        try:
            has_children = source_model.hasChildren(current_index)
        except TypeError:
            has_children = False

        if has_children:
            matches = False
        else:
            matches = self._match(current_index)

        if not matches and has_children:
            for row in range(source_model.rowCount(current_index)):
                if self.filterAcceptsRow(row, current_index):
                    return True

        return matches

    def lessThan(self, source_left, source_right):
        if not self._pattern:
            return source_left.row() > source_right.row()

        text1 = source_left.data(self._comp_text_role)
        text2 = source_right.data(self._comp_text_role)

        if self.sortCaseSensitivity() == Qt.CaseInsensitive:
            weight1 = fuzzyMatchWeight(self._pattern_case_insensitive, text1.lower())
            weight2 = fuzzyMatchWeight(self._pattern_case_insensitive, text2.lower())
        else:
            weight1 = fuzzyMatchWeight(self._pattern, text1)
            weight2 = fuzzyMatchWeight(self._pattern, text2)

        return weight1 < weight2

    def __getattr__(self, attr_name):
        return self.sourceModel().__getattribute__(attr_name)
