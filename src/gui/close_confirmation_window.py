from PyQt5 import QtWidgets as QtW
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from settings import Settings
from database import FlightStatistics


class CloseConfirmationWindow(QtW.QWidget):
    def __init__(self, parent):
        super().__init__()

        self.__parent = parent
        self.__layout = QtW.QGridLayout()

        label_confirm = QtW.QLabel('There are unclosed flights. Please confirm you want exit.'
                                   '\nWARNING: you won\'t be able to continue current flight!')
        label_confirm_font = label_confirm.font()
        label_confirm_font.setPixelSize(22)
        label_confirm.setFont(label_confirm_font)

        button_confirm = QtW.QPushButton('Confirm', self)
        button_confirm.setProperty('color', 'color_red')
        button_confirm.clicked.connect(self.__close)

        button_cancel = QtW.QPushButton('Cancel', self)
        button_cancel.clicked.connect(self.close)

        button_confirm.setCursor(QCursor(Qt.PointingHandCursor))
        button_cancel.setCursor(QCursor(Qt.PointingHandCursor))

        self.__layout.addWidget(label_confirm, 0, 0, 1, 2, Qt.AlignCenter)
        self.__layout.addWidget(button_confirm, 1, 0)
        self.__layout.addWidget(button_cancel, 1, 1)

        self.setWindowModality(Qt.WindowModality(2))
        self.setFixedSize(590, 300)
        self.setWindowTitle('Exit confirmation')
        self.setLayout(self.__layout)
        self.setStyleSheet(Settings().style)

    def __close(self):
        FlightStatistics.close_flight()
        self.close()
        self.__parent.close()

