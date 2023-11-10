import sys
from functools import partial
import typing
from PyQt6 import QtCore, QtGui

from PyQt6.QtCore import QCoreApplication, QProcess, QSettings, Qt
from PyQt6.QtGui import (QColor, QCursor, QIcon, QKeyEvent, QMovie, QPainter,
                         QPixmap, QResizeEvent)
from PyQt6.QtWidgets import (QApplication, QLabel, QWidget, QPushButton,
                             QVBoxLayout, QHBoxLayout, QFormLayout, QMenu, QMessageBox,
                             QSpinBox, QSplitter, QLineEdit, QTabWidget, QGroupBox, QDateEdit)
from PyQt6.sip import delete
from PyQt6.QtGui import QAction, QIcon, QFont

from .controller import Controller


class LineWidget(QWidget):
    def __init__(self,
                 *args,
                 ctrl: Controller,
                 category: str,
                 group: str,
                 element: str,
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.ctrl = ctrl
        self.category = category
        self.group = group
        self.element = element
        info = self.ctrl.get_element_data(
            self.category, self.group, self.element)
        self.name = info['name']
        self.default = info['default']
        self.type = info['type']
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        font = self.font()
        font.setBold(False)
        self.setFont(font)

        label = QLabel(self.name)
        label.setMinimumWidth(100)
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        if self.type == 'date':
            self.data_widget = QDateEdit()
        else:
            self.data_widget = QLineEdit(str(self.default))
        layout.addWidget(label, 1)
        layout.addWidget(self.data_widget, 3)


class GroupBox(QGroupBox):
    def __init__(
            self, *args, ctrl: Controller, category: str, group: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctrl = ctrl
        self.category = category
        self.group = group
        self.initUI()

    def initUI(self):
        font = self.font()
        font.setBold(True)
        self.setFont(font)
        self.setTitle(self.group)

        layout = QFormLayout(self)
        self.setLayout(layout)

        for element in self.ctrl.get_element_names(self.category, self.group):
            layout.addWidget(
                LineWidget(ctrl=self.ctrl, category=self.category, group=self.group, element=element))


class GroupBoxesWidget(QWidget):
    def __init__(self, *args, ctrl: Controller, category: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctrl = ctrl
        self.category = category
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        self.setLayout(layout)
        for group in self.ctrl.get_group_names(self.category):
            layout.addWidget(
                GroupBox(ctrl=self.ctrl, category=self.category, group=group))


class TabWidget(QTabWidget):
    def __init__(self, *args, ctrl: Controller, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctrl = ctrl
        self.initUI()

    def initUI(self):
        self.setTabPosition(QTabWidget.TabPosition.North)
        for category in self.ctrl.get_category_names():
            self.addTab(GroupBoxesWidget(
                ctrl=self.ctrl, category=category), category)
