from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTabWidget, QToolTip, QVBoxLayout,
                             QWidget)

from .controller import Controller, ElementData
from functools import partial

class LineWidget(QWidget):
    def __init__(self,
                 *args,
                 ctrl: Controller,
                 element_data: ElementData,
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.ctrl = ctrl
        self.element: ElementData = element_data

        self.default_palette_color = self.palette().color(QPalette.ColorRole.Text)

        if self.element.widget is None:
            self.element.widget = self

        self.initUI()

    def initUI(self):
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        font = self.font()
        font.setBold(False)
        self.setFont(font)

        self.label = QLabel(self.element.element_name)
        self.label.setMinimumWidth(100)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.input_widget = QLineEdit(str(self.element.data))
        self.input_widget.setEnabled(self.element.is_input)

        if self.element.type == 'volts':
            self.input_widget.textChanged.connect(self.is_num)
        elif self.element.type == 'date':
            self.input_widget.textChanged.connect(self.is_data)
        else:
            self.input_widget.textChanged.connect(self.is_hex)
        layout.addWidget(self.label)
        layout.addWidget(self.input_widget)

        if self.element.type == 'volts':
            self.convert_input_widget = QLineEdit(
                str(self.ctrl.volts_to_int(self.element.data))
            )
            self.convert_input_widget.setEnabled(False)
            layout.addWidget(self.convert_input_widget)

    def get_input_data(self):
        self.element.data = self.input_widget.text()
        return self.element

    def is_data(self):
        new_date = self.input_widget.text()
        new_date = new_date.replace(',', '.')
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
            new_data = float(self.input_widget.text().replace(',', '.'))
            num = self.ctrl.volts_to_int(new_data)
            if num < 0 or num > 65535:
                raise ValueError
            self.convert_input_widget.setText(str(num))
        except:
            self.set_red_widget_border_color(True)
        else:
            self.set_red_widget_border_color(False)
            self.element.data = new_data

    def is_hex(self):
        try:
            text = self.input_widget.text()
            if len(text) != 4:
                raise ValueError
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
        if param and self.element.tooltip:
            QToolTip.showText(
                self.input_widget.mapToGlobal(
                    self.input_widget.rect().bottomLeft()),
                self.element.tooltip
            )
        else:
            QToolTip.hideText()
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
        self.main_window = self.ctrl.parent
        self.category_name = category_name
        self.group_name = group_name
        self.widgets = []
        self.initUI()

    def initUI(self):
        font = self.font()
        font.setBold(True)
        self.setFont(font)
        self.setTitle(self.group_name)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        headers_layout = QHBoxLayout()
        layout.addLayout(headers_layout)
        label_name = QLabel('Элемент')
        label_value = QLabel('Значение')

        headers_layout.addWidget(label_name)
        headers_layout.addWidget(label_value)

        for element_name in self.ctrl.get_element_names(self.category_name, self.group_name):
            element_data = self.ctrl.get_element_data(
                self.category_name, self.group_name, element_name
            )
            line_widget = LineWidget(
                ctrl=self.ctrl,
                element_data=element_data
            )
            layout.addWidget(line_widget)
            self.widgets.append(line_widget)
        
        self.send_button = QPushButton('Отправить данные')
        self.send_button.clicked.connect(self.send_data)
        layout.addWidget(self.send_button)
        
        self.eeprom_commands = self.ctrl.get_eeprom_command(self.category_name, self.group_name)
        if self.eeprom_commands:
            self.apply_button = QPushButton('Отправить данные в Eeprom')
            self.apply_button.clicked.connect(self.send_eeprom)
            layout.addWidget(self.apply_button)

    def get_data_from_widgets(self):
        return [widget.get_input_data() for widget in self.widgets]

    def update_data_widgets(self):
        for widget in self.widgets:
            widget.udpate_data()
            
    def send_data(self):
        data = self.get_data_from_widgets()
        self.main_window.start_sending(data)
    
    def send_eeprom(self):
        self.main_window.start_sending(self.eeprom_commands, mode='eeprom')

    
    def block_buttons(self, value):
        if 'apply_button' in dir(self):
            self.apply_button.setDisabled(value)
        self.send_button.setDisabled(value)


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


class DebugWidget(QWidget):
    def __init__(self, *args, parent, ctrl: Controller, default_value=None):
        super().__init__(*args)
        self.parent = parent
        self.ctrl = ctrl
        self.main_window = self.ctrl.parent
        self.widgets: list = []
        if default_value is None:
            default_value = ['53', '08', '', '', '', '', '',]
        self.default_value = default_value
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout(self)

        layout.addWidget(QLabel('Команда: '))
        for val in self.default_value:
            line_edit = QLineEdit()
            line_edit.setFixedWidth(30)
            line_edit.setText(val)
            layout.addWidget(line_edit)
            self.widgets.append(line_edit)
            line_edit.textChanged.connect(partial(self.input_handler, line_edit))

        layout.addWidget(QLabel('КС: '))

        self.checksum_line_edit = QLineEdit('')
        self.checksum_line_edit.setFixedWidth(30)
        self.checksum_line_edit.setDisabled(True)
        layout.addWidget(self.checksum_line_edit)
        self.input_handler(self.checksum_line_edit)

        layout.addSpacing(30)

        self.send_button = QPushButton('Отправить')
        self.send_button.clicked.connect(self.send_data)
        layout.addWidget(self.send_button)
        
        layout.addSpacing(30)

        destroy_button = QPushButton('-')
        destroy_button.clicked.connect(self.destroy_widget)
        destroy_button.setFixedWidth(30)
        layout.addWidget(destroy_button)

        layout.addStretch(1)

    def send_data(self):
        data = self.get_data_from_widgets()
        self.main_window.start_sending([data], mode='debug')
        
    def get_data_from_widgets(self):
        data = []
        for line_edit in self.widgets:
            data.append(line_edit.text())
        data.append(self.checksum_line_edit.text())
        return data
    
    def destroy_widget(self):
        self.parent.remove_widget(self)
        self.deleteLater()

    def input_handler(self, widget):
        widget_text = widget.text()
        if widget_text:
            try:
                num = int(widget_text, 16)
                if num < 0 or num > 255:
                    widget.setText(widget_text[:2])
            except:
                widget.setText(widget_text[:-1])
                self.input_handler(widget)
        try:
            summ = sum(
                [int(line_edit.text(), 16) for line_edit in self.widgets if line_edit.text()]) & 0xff
            self.checksum_line_edit.setText(f'{summ:02X}')
        except:
            self.checksum_line_edit.setText('')
            
    def block_button(self, value: bool):
        self.send_button.setDisabled(value)


class DebugTabWidget(QWidget):
    def __init__(self, *args, ctrl: Controller, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctrl = ctrl
        self.main_window = self.ctrl.parent
        self.widgets: list = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        self.widgets_layout = QVBoxLayout()
        layout.addLayout(self.widgets_layout)
        self.widgets_layout.setSpacing(0)
        
        for value in self.main_window.settings.value('default_debug'):
            debug_widget = DebugWidget(parent=self, ctrl=self.ctrl, default_value=value)
            self.widgets_layout.addWidget(debug_widget)
            self.widgets.append(debug_widget)
        
        add_widget_button = QPushButton('+')
        add_widget_button.clicked.connect(self.add_widget)
        add_widget_button.setFixedWidth(30)
        layout.addWidget(add_widget_button)

        layout.addStretch(1)

        self.send_button = QPushButton('Отправить все команды')
        self.send_button.clicked.connect(self.send_data)
        layout.addWidget(self.send_button)


    def remove_widget(self, widget):
        self.widgets.remove(widget)
    
    def add_widget(self):
        debug_widget = DebugWidget(parent=self, ctrl=self.ctrl)
        debug_widget.block_button(not self.main_window.serial_port.isOpen())
        self.widgets_layout.addWidget(debug_widget)
        self.widgets.append(debug_widget)
        
        
    def block_buttons(self, value: bool):
        self.send_button.setDisabled(value)
        for widget in self.widgets:
            widget.block_button(value)
            
    def get_data_from_widgets(self):
        return [widget.get_data_from_widgets() for widget in self.widgets]
    
    def send_data(self):
        data = self.get_data_from_widgets()
        self.main_window.start_sending(data, mode='debug')

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

        self.debug_widget = DebugTabWidget(ctrl=self.ctrl)
        self.addTab(self.debug_widget, 'Окно отладки')

    def get_data_from_widgets(self):
        result = []
        for widget in self.widgets:
            result.extend(widget.get_data_from_widgets())
        return result
    
    def get_data_from_debug(self):
        return self.debug_widget.get_data_from_widgets()

    def block_buttons(self, value: bool):
        for widget in self.widgets:
            widget.block_buttons(value)
        self.debug_widget.block_buttons(value)

    def update_data_widgets(self):
        for widget in self.widgets:
            widget.update_data_widgets()
