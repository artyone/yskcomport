from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (QFormLayout, QGroupBox, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTabWidget, QVBoxLayout,
                             QWidget)

from .controller import Controller, ElementData


class LineWidget(QWidget):
    def __init__(self,
                 *args,
                 ctrl: Controller,
                 category_name: str,
                 group_name: str,
                 element_name: str,
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.ctrl = ctrl
        self.category_name = category_name
        self.group_name = group_name
        self.element_name = element_name
        self.default_palette_color = self.palette().color(QPalette.ColorRole.Text)

        self.element: ElementData = self.ctrl.get_element_data(
            self.category_name, self.group_name, self.element_name
        )
        if self.element.widget is None:
            self.element.widget = self

        self.initUI()

    def initUI(self):
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        font = self.font()
        font.setBold(False)
        self.setFont(font)

        label = QLabel(self.element.element_name)
        label.setMinimumWidth(100)
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.input_widget = QLineEdit(str(self.element.data))
        self.input_widget.setEnabled(self.element.is_input)

        if self.element.type == 'volts':
            self.input_widget.textChanged.connect(self.is_num)
        elif self.element.type == 'date':
            self.input_widget.textChanged.connect(self.is_data)
        else:
            self.input_widget.textChanged.connect(self.is_hex)
        layout.addWidget(label)
        layout.addWidget(self.input_widget)

    def get_input_data(self):
        self.element.data = self.input_widget.text()
        return self.element

    def is_data(self):
        new_date = self.input_widget.text()
        try:
            date_format = "%d.%m.%y"
            datetime.strptime(new_date, date_format)
        except:
            self.set_red_widget_border_color(True)
        else:
            self.set_red_widget_border_color(False)
            self.element.data = new_date

    def is_num(self):
        try:
            new_data = float(self.input_widget.text())
            num = self.ctrl.volts_to_int(new_data)
            if num < 0 or num > 65535:
                raise ValueError
        except:
            self.set_red_widget_border_color(True)
        else:
            self.set_red_widget_border_color(False)
            self.element.data = new_data

    def is_hex(self):
        try:
            new_data = int(self.input_widget.text(), base=16)
            if new_data < 0 or new_data > 65535:
                raise ValueError
        except:
            self.set_red_widget_border_color(True)
        else:
            self.set_red_widget_border_color(False)
            self.element.data = new_data

    def set_red_widget_border_color(self, param):
        border = "QLineEdit { border: 1px solid red; }" if param else ''
        self.input_widget.setStyleSheet(border)
        self.ctrl.parent.tabs.block_buttons(param)

    def update_data(self):
        if not self.element.is_input:
            self.input_widget.setEnabled(True)
            self.input_widget.setText(str(self.element.data))
            self.input_widget.setEnabled(False)


class GroupBox(QGroupBox):
    def __init__(
            self,
            *args,
            ctrl: Controller,
            category_name: str,
            group_name: str,
            **kwargs):
        super().__init__(*args, **kwargs)
        self.ctrl = ctrl
        self.category_name = category_name
        self.group_name = group_name
        self.widgets = []
        self.initUI()

    def initUI(self):
        font = self.font()
        font.setBold(True)
        self.setFont(font)
        self.setTitle(self.group_name)

        layout = QFormLayout(self)

        for element in self.ctrl.get_element_names(self.category_name, self.group_name):
            line_widget = LineWidget(
                ctrl=self.ctrl,
                category_name=self.category_name,
                group_name=self.group_name,
                element_name=element
            )
            layout.addRow(line_widget)
            self.widgets.append(line_widget)

    def get_data_from_widgets(self):
        return [widget.get_input_data() for widget in self.widgets]

    def update_data_widgets(self):
        for widget in self.widgets:
            widget.udpate_data()


class GroupBoxesWidget(QWidget):
    def __init__(self, *args, ctrl: Controller, category: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctrl = ctrl
        self.category = category
        self.main_window = self.ctrl.parent
        self.widgets: list[GroupBox] = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        gb_layout = QHBoxLayout()
        layout.addLayout(gb_layout)

        for group in self.ctrl.get_group_names(self.category):
            gb = GroupBox(ctrl=self.ctrl,
                          category_name=self.category, group_name=group)
            gb_layout.addWidget(gb)
            self.widgets.append(gb)

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

    def update_data_widgets(self):
        for widget in self.widgets:
            widget.update_data_widgets()


class TabWidget(QTabWidget):
    def __init__(self, *args, ctrl: Controller, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctrl = ctrl
        self.widgets: list[GroupBoxesWidget] = []
        self.initUI()

    def initUI(self):
        self.setTabPosition(QTabWidget.TabPosition.North)
        for category in self.ctrl.get_category_names():
            widget = GroupBoxesWidget(
                ctrl=self.ctrl,
                category=category
            )
            self.addTab(widget, category)
            self.widgets.append(widget)

    def get_data_from_widgets(self):
        result = []
        for widget in self.widgets:
            result.extend(widget.get_data_from_widgets())
        return result

    def block_buttons(self, value: bool):
        for widget in self.widgets:
            widget.block_buttons(value)

    def update_data_widgets(self):
        for widget in self.widgets:
            widget.update_data_widgets()
