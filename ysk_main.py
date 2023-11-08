import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel



def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main_window = QMainWindow()
    main_window.setCentralWidget(QLabel('Hello World!'))
    main_window.show()
    app.exec()


if __name__ == '__main__':
    main()
