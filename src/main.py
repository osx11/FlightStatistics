from PyQt5 import QtWidgets as QtW
from gui.main_window import MainWindow
from sys import argv
from database import create_tables
from datareceiver import DataReceiver
from threading import Thread


if __name__ == '__main__':
    create_tables()

    app = QtW.QApplication(argv)
    main = MainWindow()

    receiver = DataReceiver('127.0.0.1', 50000)
    Thread(target=receiver.run, daemon=True).start()

    exit(app.exec())
