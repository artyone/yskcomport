import sys
import typing
from functools import partial
from typing import NamedTuple

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import QCoreApplication, QProcess, QSettings, Qt
from PyQt6.QtGui import (QAction, QColor, QCursor, QFont, QIcon, QKeyEvent,
                         QMovie, QPainter, QPixmap, QResizeEvent)
from PyQt6.QtWidgets import (QApplication, QDateEdit, QFormLayout, QGroupBox,
                             QHBoxLayout, QLabel, QLineEdit, QMenu,
                             QMessageBox, QPushButton, QSpinBox, QSplitter,
                             QTabWidget, QVBoxLayout, QWidget)
from PyQt6.sip import delete

from .controller import Controller


class ElementData(NamedTuple):
    category: str
    group: str
    element: str
    data: str

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

    def get_input_data(self):
        return ElementData(self.category, self.group, self.element, self.data_widget.text())


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

        self.widgets = [
            LineWidget(ctrl=self.ctrl, category=self.category, group=self.group, element=element)
            for element in self.ctrl.get_element_names(self.category, self.group)
        ]

        for widget in self.widgets:
            layout.addWidget(widget)

    def get_data_from_widgets(self):
        return [widget.get_input_data() for widget in self.widgets]


class GroupBoxesWidget(QWidget):
    def __init__(self, *args, ctrl: Controller, category: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctrl = ctrl
        self.category = category
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.widgets = [
            GroupBox(ctrl=self.ctrl, category=self.category, group=group)
            for group in self.ctrl.get_group_names(self.category)
        ]

        for widget in self.widgets:
            layout.addWidget(widget)
        
    def get_data_from_widgets(self):
        result = []
        for widget in self.widgets:
            result.extend(widget.get_data_from_widgets())
        return result


class TabWidget(QTabWidget):
    def __init__(self, *args, ctrl: Controller, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctrl = ctrl
        self.initUI()

    def initUI(self):
        self.setTabPosition(QTabWidget.TabPosition.North)
        self.widgets = [
            GroupBoxesWidget(ctrl=self.ctrl, category=category)
            for category in self.ctrl.get_category_names()
        ]
        for widget in self.widgets:
            self.addTab(widget, widget.category)
        
    def get_data_from_widgets(self):
        result = []
        for widget in self.widgets:
            result.extend(widget.get_data_from_widgets())
        return result
            
    
