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

try:
    from PyQt5.QtGui import Qt, QImage, QPixmap
    from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFileDialog
except ImportError:
    from PySide2.QtGui import Qt, QImage, QPixmap
    from PySide2.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFileDialog

import hou

from .input_field import InputField


class IconField(QWidget):
    def __init__(self, initial_icon_name=''):
        super(IconField, self).__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.text_field = InputField(initial_icon_name)
        layout.addWidget(self.text_field)

        self.icon_preview = QLabel()
        self.icon_preview.setToolTip('Icon preview')
        self.icon_preview.setFixedSize(24, 24)
        self.icon_preview.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_preview)
        self.text_field.textChanged.connect(self.updateIconPreview)

        self.pick_from_disk_button = QPushButton()
        self.pick_from_disk_button.setToolTip('Pick icon from disk')
        self.pick_from_disk_button.setFixedSize(24, 24)
        self.pick_from_disk_button.setIcon(hou.qt.Icon('BUTTONS_chooser_file', 16, 16))
        self.pick_from_disk_button.clicked.connect(self.pickIconFromDisk)
        layout.addWidget(self.pick_from_disk_button)

        self.pick_from_houdini_button = QPushButton()
        self.pick_from_houdini_button.setToolTip('Pick icon from Houdini')
        self.pick_from_houdini_button.setFixedSize(24, 24)
        self.pick_from_houdini_button.setIcon(hou.qt.Icon('OBJ_hlight', 16, 16))
        self.pick_from_houdini_button.clicked.connect(self.pickIconFromHoudini)
        layout.addWidget(self.pick_from_houdini_button)

    def text(self):
        return self.text_field.text()

    def setText(self, text):
        self.text_field.setText(text)
        self.updateIconPreview()

    def icon(self):
        raise NotImplementedError

    def setIcon(self, name):
        if name is None:
            self.text_field.setText('')

        raise NotImplementedError

    def updateIconPreview(self):
        icon_file_name = self.text_field.text()

        if not icon_file_name:
            self.icon_preview.clear()
            return

        if os.path.isfile(icon_file_name):  # Todo: Limit allowed file size
            _, ext = os.path.splitext(icon_file_name)
            if ext in ('.jpg', '.jpeg', '.png', '.bmp', '.tga', '.tif', '.tiff'):
                image = QImage(icon_file_name)
                self.icon_preview.setPixmap(QPixmap.fromImage(image).scaled(24, 24, Qt.KeepAspectRatio))
            else:  # Fallback to Houdini loading
                with hou.undos.disabler():
                    try:
                        comp_net = hou.node('/img/').createNode('img')
                        file_node = comp_net.createNode('file')
                        file_node.parm('filename1').set(icon_file_name)

                        # Todo: Support alpha channel
                        image_data = file_node.allPixelsAsString(depth=hou.imageDepth.Int8)
                        image = QImage(image_data, file_node.xRes(), file_node.yRes(), QImage.Format_RGB888)

                        self.icon_preview.setPixmap(QPixmap.fromImage(image).scaled(24, 24, Qt.KeepAspectRatio))
                    except hou.OperationFailed:
                        self.icon_preview.clear()
                    finally:
                        comp_net.destroy()
        else:
            try:
                icon = hou.qt.Icon(icon_file_name, 24, 24)
                self.icon_preview.setPixmap(icon.pixmap(24, 24))
            except hou.OperationFailed:
                self.icon_preview.clear()

    def pickIconFromDisk(self):
        path = self.text_field.text()
        if os.path.isdir(path):
            initial_dir = path
        elif os.path.isfile(path):
            initial_dir = os.path.dirname(path)
        else:
            initial_dir = os.path.dirname(hou.hipFile.path())

        icon_file_name, _ = QFileDialog.getOpenFileName(self, 'Pick Icon', initial_dir,
                                                        filter='Images (*.pic *.pic.Z *.picZ *.pic.gz *.picgz *.rat '
                                                               '*.tbf *.dsm *.picnc *.piclc *.rgb *.rgba *.sgi *.tif '
                                                               '*.tif3 *.tif16 *.tif32 *.tiff *.yuv *.pix *.als *.cin '
                                                               '*.kdk *.exr *.psd *.psb *.si *.tga *.vst *.vtg *.rla '
                                                               '*.rla16 *.rlb *.rlb16 *.hdr *.ptx *.ptex *.ies *.dds '
                                                               '*.qtl *.pic *.pic.Z *.pic.gz *.jpg *.jpeg *.bmp *.png '
                                                               '*.svg *.);;'
                                                               'All (*.*)')
        if icon_file_name:
            self.text_field.setText(icon_file_name)

    def pickIconFromHoudini(self):
        from ..icon_list import IconListWindow

        icon_file_name = IconListWindow.getIconName(self, 'Pick Icon', self.text_field.text())
        if icon_file_name:
            self.text_field.setText(icon_file_name)
