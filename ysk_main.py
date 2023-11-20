import sys

from PyQt5.QtWidgets import QApplication

from app import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main_window = MainWindow(app=app)
    main_window.show()
    app.exec_()

if __name__ == '__main__':
    main()
