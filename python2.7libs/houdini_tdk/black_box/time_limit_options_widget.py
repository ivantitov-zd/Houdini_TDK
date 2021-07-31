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
    from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox, QDateTimeEdit, QSpacerItem, QSizePolicy
    from PyQt5.QtCore import Qt, QDate
except ImportError:
    from PySide2.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox, QDateTimeEdit, QSpacerItem, QSizePolicy
    from PySide2.QtCore import Qt, QDate


class TimeLimitOptionsWidget(QWidget):
    def __init__(self):
        super(TimeLimitOptionsWidget, self).__init__()

        layout = QGridLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.use_time_limit_toggle = QCheckBox('Use time limit')
        self.use_time_limit_toggle.setChecked(False)
        layout.addWidget(self.use_time_limit_toggle, 0, 0, 1, -1)

        self.start_date_label = QLabel('Start date')
        layout.addWidget(self.start_date_label, 1, 0)

        self.start_date_field = QDateTimeEdit(QDate.currentDate())
        self.start_date_field.setMinimumDate(QDate.currentDate())
        self.start_date_field.setDisplayFormat('yyyy.MM.dd')
        self.start_date_field.setCalendarPopup(True)
        self.start_date_field.setDisabled(True)
        self.use_time_limit_toggle.toggled.connect(self.start_date_field.setEnabled)
        layout.addWidget(self.start_date_field, 1, 1, 1, -1)

        self.end_date_label = QLabel('End date')
        layout.addWidget(self.end_date_label, 2, 0)

        self.end_date_field = QDateTimeEdit(QDate.currentDate())
        self.end_date_field.setMinimumDate(QDate.currentDate())
        self.end_date_field.setDisplayFormat('yyyy.MM.dd')
        self.end_date_field.setCalendarPopup(True)
        self.end_date_field.setDisabled(True)
        self.use_time_limit_toggle.toggled.connect(self.end_date_field.setEnabled)
        layout.addWidget(self.end_date_field, 2, 1, 1, -1)

        self.range_label = QLabel('1 day')
        self.range_label.setAlignment(Qt.AlignCenter)
        self.start_date_field.dateChanged.connect(self._updateRangeLabel)
        self.end_date_field.dateChanged.connect(self._updateRangeLabel)
        layout.addWidget(self.range_label, 3, 0, 1, -1)

        self.spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        layout.addItem(self.spacer, 4, 0, 1, -1)

    def _updateRangeLabel(self):
        start_date = self.start_date_field.date()
        end_date = self.end_date_field.date()

        days = start_date.daysTo(end_date) + 1
        text = '{} day{}'.format(days, 's' * (days > 1))
        self.range_label.setText(text)
