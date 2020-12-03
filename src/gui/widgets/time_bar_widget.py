from PyQt5 import QtWidgets as QtW
from PyQt5 import QtGui
from PyQt5.QtCore import Qt


class TimeBarWidget(QtW.QWidget):
    def __init__(self, text):
        super().__init__()

        self.__text = text

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.__draw(qp, event.rect())
        qp.end()

    def __draw(self, qp, event_rect):
        coords = event_rect.getCoords()

        qp.setPen(QtGui.QColor(255, 100, 184))
        qp.setBrush(QtGui.QColor(255, 100, 184))
        qp.drawRect(event_rect)

        qp.setPen(QtGui.QColor(255, 0, 0))
        qp.setBrush(QtGui.QColor(255, 0, 0))

        qp.drawRect(coords[0], coords[1], coords[2], 5)

        qp.setPen(QtGui.QColor(0, 0, 0))
        qp.setBrush(QtGui.QColor(0, 0, 0))

        qp.drawText(event_rect, Qt.AlignCenter, self.__text)
