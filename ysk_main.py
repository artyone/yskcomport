import sys

from PyQt5.QtWidgets import QApplication

from app import MainWindow


def main() -> None:
    with QApplication(sys.argv) as app:
        main_window = MainWindow(app=app)
        main_window.show()
        app.exec()


if __name__ == '__main__':
    main()
