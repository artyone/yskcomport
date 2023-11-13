import sys

from icecream import install
from PyQt6.QtWidgets import QApplication

from app import MainWindow

install()


def main() -> None:
    app = QApplication(sys.argv)
    main_window = MainWindow(app=app)
    main_window.show()
    app.exec()


if __name__ == '__main__':
    main()
