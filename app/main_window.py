import sys

from PyQt5.QtCore import (QByteArray, QCoreApplication, QIODevice, QProcess,
                          QSettings, QTime, QTimer)
from PyQt5.QtGui import (QCloseEvent, QColor, QIcon, QTextCharFormat,
                         QTextCursor)
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
                             QMainWindow, QMessageBox, QPlainTextEdit,
                             QProgressBar, QPushButton, QSplitter, QVBoxLayout,
                             QWidget)

from .controller import AnswerException, Controller
from .tab_widgets import TabWidget
from time import sleep


class MainWindow(QMainWindow):
    def __init__(self, *args, app: QApplication, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.app = app
        self.app.setStyle('Fusion')

        self.settings = QSettings('radiopribor', 'YSK')

        if self.settings.value('geometry') is None:
            self.settings.setValue('geometry', self.saveGeometry())
        if self.settings.value('default_debug') is None:
            self.settings.setValue('default_debug', [
                ['53', '08', '', '', '', '', '',]
            ])

        geometry = self.settings.value('geometry')
        self.restoreGeometry(geometry)

        self.app.setWindowIcon(QIcon('icon.ico'))
        self.setWindowTitle('YSK, ver. 24.03.29')

        self.serial_port = QSerialPort(self)
        self.serial_port.readyRead.connect(self.read_data)
        self.buffer_answer = QByteArray()

        try:
            self.ctrl = Controller(self)
        except Exception as e:
            if self.show_message_box('Ошибка файла json, восстановить файл по-умолчанию?'):
                Controller.generate_json()
                self.ctrl = Controller(self)
            else:
                sys.exit()

        self.initUI()

    def initUI(self) -> None:
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout(main_widget)

        self.port_combobox = PortComboBox(self)
        self.main_layout.addWidget(self.port_combobox)
        self.update_port_list()
        self.port_combobox.currentIndexChanged.connect(self.close_serial_port)

        open_close_layout = QHBoxLayout()
        self.open_port_button = QPushButton('Открыть COM-порт', self)
        self.open_port_button.clicked.connect(self.open_serial_port)
        self.close_port_button = QPushButton('Закрыть COM-порт', self)
        self.close_port_button.clicked.connect(self.close_serial_port)
        open_close_layout.addWidget(self.open_port_button)
        open_close_layout.addWidget(self.close_port_button)
        self.main_layout.addLayout(open_close_layout)

        splitter = QSplitter()

        self.tabs = TabWidget(ctrl=self.ctrl)
        right_block = self.get_right_block()

        splitter.addWidget(self.tabs)
        splitter.addWidget(right_block)

        self.main_layout.addWidget(splitter)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.send_next_command)

        self.tabs.block_buttons(True)

    def resizeEvent(self, a0) -> None:
        self.settings.setValue('geometry', self.saveGeometry())
        return super().resizeEvent(a0)

    def moveEvent(self, a0) -> None:
        self.settings.setValue('geometry', self.saveGeometry())
        return super().moveEvent(a0)

    def get_right_block(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        filter_layout = QHBoxLayout()
        layout.addLayout(filter_layout)

        self.filter_combobox = QComboBox()
        self.filter_combobox.addItems(['Нет', 'Не показывать 0F', 'Полный режим'])
        filter_layout.addWidget(QLabel('Фильтр лога: '))
        filter_layout.addWidget(self.filter_combobox)

        clear_log_btn = QPushButton('Очистить лог')
        clear_log_btn.clicked.connect(self.clear_log)
        filter_layout.addWidget(clear_log_btn)

        self.log_widget = QPlainTextEdit()
        self.log_widget.setMinimumWidth(350)
        layout.addWidget(self.log_widget)
        return widget

    def clear_log(self):
        self.log_widget.clear()

    def start_sending(self, widget_datas, mode=None):
        if not self.serial_port.isOpen():
            self.set_console_text('Необходимо открыть порт', 'error')
            return

        if mode == 'debug':
            self.commands = self.ctrl.get_commands_debug(widget_datas)
        elif mode == 'eeprom':
            self.commands = self.ctrl.get_commands_for_eeprom(widget_datas)
        else:
            self.commands = self.ctrl.get_data_for_temp_memory(widget_datas)

        self.current_index = 0

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(len(self.commands))
        self.main_layout.addWidget(self.progress_bar)

        self.block_all_elements(True)
        self.timer.start(250)

    def send_next_command(self):
        if self.current_index >= len(self.commands):
            self.timer.stop()
            self.block_all_elements(False)
            self.set_console_text(f'Команд отправлено: {len(self.commands)}')
            self.progress_bar.deleteLater()
            return

        command = self.commands[self.current_index]
        self.serial_port.write(command)
        self.current_index += 1
        self.progress_bar.setValue(self.current_index)
        self.set_console_text(
            f'Команда отправлена: {self.command_byte_to_str(command)}')

    def block_all_elements(self, value: bool):
        self.open_port_button.setDisabled(value)
        self.close_port_button.setDisabled(value)
        self.port_combobox.setDisabled(value)
        self.tabs.block_buttons(value)

    @staticmethod
    def command_byte_to_str(command: bytes):
        formatted_command = ' '.join(
            [command.hex().upper()[i:i+2] for i in range(0, len(command.hex()), 2)])
        return formatted_command


    def read_data(self):
        while self.serial_port.waitForReadyRead(100):
            data = self.serial_port.readAll()
            data = self.check_answer(data)
            if data is None:
                continue
            try:
                widget = self.ctrl.get_element_from_answer(data)
            except AnswerException as e:
                self.set_console_text(str(e), 'error')
                continue
            widget.update_data()

    def check_answer(self, answer):
        self.buffer_answer += answer
        if self.filter_combobox.currentIndex() == 2:
            self.set_console_text(
                    f"Приняты данные:        {self.command_byte_to_str(answer.data())}"
                )
        while len(self.buffer_answer) >= 8:
            if self.buffer_answer[0:2] == b'\x53\x08':
                if self.filter_combobox.currentIndex() == 1 and self.buffer_answer[2:4] == b'\x54\x0f':
                    self.buffer_answer = self.buffer_answer[8:]
                    continue
                result = self.buffer_answer = self.buffer_answer[:8]
                if self.filter_combobox.currentIndex() != 2:
                    self.set_console_text(
                        f"Приняты данные:        {self.command_byte_to_str(result.data())}"
                    )
                self.buffer_answer = self.buffer_answer[8:]
                return result
            self.buffer_answer = self.buffer_answer[1:]
        return None

    def restart_app(self) -> None:
        program = sys.executable
        QProcess.startDetached(program, sys.argv)
        QCoreApplication.quit()

    def show_message_box(self, message: str) -> bool:
        reply = QMessageBox.question(self, 'Предупреждение', message,
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.Yes)

        if reply == QMessageBox.StandardButton.Yes:
            return True
        else:
            return False

    def update_port_list(self):
        self.port_list = QSerialPortInfo.availablePorts()
        self.port_combobox.clear()
        self.port_combobox.addItems(
            [f'{port.description()} ({port.portName()})' for port in self.port_list])

    def open_serial_port(self):
        if self.serial_port.isOpen():
            self.set_console_text(
                f'Порт {self.serial_port.portName()} уже открыт.')
            return

        port_name = self.port_combobox.currentIndex()
        self.serial_port.setPortName(self.port_list[port_name].portName())
        self.serial_port.setBaudRate(115200)

        is_open_port = self.serial_port.open(QIODevice.OpenModeFlag.ReadWrite)
        if is_open_port:
            self.set_console_text(
                f'Порт {self.serial_port.portName()} открыт.')
            self.tabs.block_buttons(False)
        else:
            self.set_console_text(
                f'Порт {self.serial_port.portName()} НЕ открыт.', 'error')
            self.tabs.block_buttons(True)

    def close_serial_port(self):
        if self.serial_port.isOpen():
            self.serial_port.close()
            self.set_console_text(
                f"Порт {self.serial_port.portName()} закрыт.")
        self.tabs.block_buttons(True)

    def set_console_text(self, text: str, type='info'):
        current_time = QTime.currentTime().toString("hh:mm:ss:zzz")
        formatted_text = f"{current_time}: {text}\n"
        text_format = QTextCharFormat()

        if type == 'error':
            text_format.setForeground(QColor('red'))

        cursor = self.log_widget.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(formatted_text, text_format)
        self.log_widget.setTextCursor(cursor)

        self.log_widget.ensureCursorVisible()

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.close_serial_port()

        default_values = self.tabs.get_data_from_debug()
        default_settings = [i[:-1] for i in default_values]
        self.settings.setValue('default_debug', default_settings)
        return super().closeEvent(a0)


class PortComboBox(QComboBox):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent

    def showPopup(self) -> None:
        self.parent.update_port_list()
        return super().showPopup()
