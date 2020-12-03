from PyQt5 import QtWidgets as QtW
from gui.main_window import MainWindow
from sys import argv
from database import create_tables


if __name__ == '__main__':
    create_tables()
    app = QtW.QApplication(argv)
    main = MainWindow()
    exit(app.exec())
