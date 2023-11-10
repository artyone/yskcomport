import sys
import typing
from functools import partial
from os.path import abspath, dirname

from PyQt6 import QtGui
from PyQt6.QtCore import QCoreApplication, QProcess, QSettings, Qt
from PyQt6.QtGui import (QAction, QColor, QCursor, QIcon, QKeyEvent,
                         QMoveEvent, QMovie, QPainter, QPixmap, QResizeEvent)
from PyQt6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
                             QMenu, QMessageBox, QPlainTextEdit, QPushButton,
                             QSpinBox, QSplitter, QStackedLayout, QVBoxLayout,
                             QWidget)
from PyQt6.sip import delete

from .controller import Controller
from .tab_widgets import TabWidget


class MainWindow(QMainWindow):
    def __init__(self, *args, app: QApplication, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.app = app
        self.app.setStyle('Fusion')

        self.settings = QSettings('radiopribor', 'YSK')

        if self.settings.value('geometry') is None:
            self.settings.setValue('geometry', self.saveGeometry())

        geometry = self.settings.value('geometry')
        self.restoreGeometry(geometry)

        self.app.setWindowIcon(QIcon('resource/vise-drawer.png'))
        self.setWindowTitle('YSK')

        try:
            self.ctrl = Controller(self)
        except Exception as e:
            print(str(e))
            if self.show_message_box('Ошибка файла json, восстановить файл по-умолчанию?'):
                Controller.generate_json()
                self.ctrl = Controller(self)
            else: 
                exit()
        
        self.initUI()

    def initUI(self) -> None:
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        splitter = QSplitter()
        self.tabs = TabWidget(ctrl=self.ctrl)
        splitter.addWidget(self.tabs)
        splitter.addWidget(QPlainTextEdit())
        main_layout.addWidget(splitter)

        self.send_temp_button = QPushButton('Отправить данные')
        self.send_temp_button.clicked.connect(self.send_to_temp_memory)
        self.apply_data_button = QPushButton('Применить')
        self.apply_data_button.clicked.connect(self.apply_data)

        main_layout.addWidget(self.send_temp_button)
        main_layout.addWidget(self.apply_data_button)


    def resizeEvent(self, a0: QResizeEvent | None) -> None:
        self.settings.setValue('geometry', self.saveGeometry())
        return super().resizeEvent(a0)

    def moveEvent(self, a0: QMoveEvent | None) -> None:
        self.settings.setValue('geometry', self.saveGeometry())
        return super().moveEvent(a0)
    
    def send_to_temp_memory(self):
        widget_datas = self.tabs.get_data_from_widgets()
        self.ctrl.send_data_to_temp_memory(widget_datas)

    def apply_data(self):
        pass
    
    def restart_app(self) -> None:
        program = sys.executable
        QProcess.startDetached(program, sys.argv)
        QCoreApplication.quit()

    def show_message_box(self, message: str) -> bool:
        reply = QMessageBox.question(self, 'Предупреждение', message,
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.Yes)

        if reply == QMessageBox.StandardButton.Yes:
            return True
        else:
            return False

