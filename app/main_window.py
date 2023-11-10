import sys
import typing
from functools import partial
from os.path import abspath, dirname

from PyQt6 import QtGui
from PyQt6.QtCore import QCoreApplication, QProcess, QSettings, Qt
from PyQt6.QtGui import (QAction, QColor, QCursor, QIcon, QKeyEvent,
                         QMoveEvent, QMovie, QPainter, QPixmap, QResizeEvent)
from PyQt6.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout,
                             QLabel, QMainWindow, QMenu, QMessageBox,
                             QPushButton, QPlainTextEdit, QSpinBox, QSplitter,
                             QStackedLayout, QWidget)
from PyQt6.sip import delete

from .controller import Controller
from .tab_widgets import TabWidget


class MainWindow(QMainWindow):
    def __init__(self, *args, app: QApplication, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.app = app
        try:
            self.ctrl = Controller()
        except Exception:
            Controller.generate_json()
            self.ctrl = Controller()

        self.settings = QSettings('radiopribor', 'YSK')

        if self.settings.value('geometry') is None:
            self.settings.setValue('geometry', self.saveGeometry())

        geometry = self.settings.value('geometry')
        self.restoreGeometry(geometry)

        self.app.setWindowIcon(QIcon('resource/vise-drawer.png'))
        self.setWindowTitle('YSK')
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

        self.apply_button = QPushButton('Отправить данные')
        self.apply_button.clicked.connect(self.restart_app)
        main_layout.addWidget(self.apply_button)



    def resizeEvent(self, a0: QResizeEvent | None) -> None:
        self.settings.setValue('geometry', self.saveGeometry())
        return super().resizeEvent(a0)

    def moveEvent(self, a0: QMoveEvent | None) -> None:
        self.settings.setValue('geometry', self.saveGeometry())
        return super().moveEvent(a0)
    
    def restart_app(self) -> None:
        program = sys.executable
        QProcess.startDetached(program, sys.argv)
        QCoreApplication.quit()

