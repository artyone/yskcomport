from typing import NamedTuple

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (QDateEdit, QFormLayout, QGroupBox, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTabWidget,
                             QVBoxLayout, QWidget)

from .controller import Controller


class ElementData(NamedTuple):
    category: str
    group: str
    element: str
    type: str
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
            self.data_widget.setDate(
                QDate.fromString(self.default, "dd.MM.yyyy"))
        else:
            self.data_widget = QLineEdit(str(self.default))
        layout.addWidget(label, 1)
        layout.addWidget(self.data_widget, 3)

    def get_input_data(self):
        return ElementData(self.category, self.group, self.element, self.type, self.data_widget.text())


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
            LineWidget(ctrl=self.ctrl, category=self.category,
                       group=self.group, element=element)
            for element in self.ctrl.get_element_names(self.category, self.group)
        ]

        for widget in self.widgets:
            layout.addWidget(widget)

    def get_data_from_widgets(self):
        return [widget.get_input_data() for widget in self.widgets]


class GroupBoxesWidget(QWidget):
    def __init__(self, *args, main_window, ctrl: Controller, category: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctrl = ctrl
        self.category = category
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        gb_layout = QHBoxLayout()
        layout.addLayout(gb_layout)

        self.widgets = [
            GroupBox(ctrl=self.ctrl, category=self.category, group=group)
            for group in self.ctrl.get_group_names(self.category)
        ]

        for widget in self.widgets:
            gb_layout.addWidget(widget)

        self.send_button = QPushButton('Отправить данные')
        self.send_button.clicked.connect(self.send_data)
        layout.addWidget(self.send_button)

        self.apply_button = QPushButton('Отправить данные в Eeprom')
        self.apply_button.clicked.connect(self.main_window.send_apply_command)
        layout.addWidget(self.apply_button)

    def get_data_from_widgets(self):
        result = []
        for widget in self.widgets:
            result.extend(widget.get_data_from_widgets())
        return result

    def send_data(self):
        data = self.get_data_from_widgets()
        self.main_window.start_sending(data)

    def block_buttons(self, value: bool):
        self.apply_button.setDisabled(value)
        self.send_button.setDisabled(value)


class TabWidget(QTabWidget):
    def __init__(self, *args, main_window, ctrl: Controller, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctrl = ctrl
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.setTabPosition(QTabWidget.TabPosition.North)
        self.widgets = [
            GroupBoxesWidget(main_window=self.main_window,
                             ctrl=self.ctrl, category=category)
            for category in self.ctrl.get_category_names()
        ]
        for widget in self.widgets:
            self.addTab(widget, widget.category)

    def get_data_from_widgets(self):
        result = []
        for widget in self.widgets:
            result.extend(widget.get_data_from_widgets())
        return result
    
    def block_buttons(self, value: bool):
        for widget in self.widgets:
            widget.block_buttons(value)
