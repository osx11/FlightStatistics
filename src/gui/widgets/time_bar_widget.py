from PyQt5 import QtWidgets as QtW
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QRect
from gui.flight_details_window import FlightDetailsWindow


class TimeBarWidget(QtW.QWidget):
    def __init__(self, text, duration, flight_id):
        super().__init__()

        self.__text = text
        self.__duration = duration
        self.__main_color, self.__top_color, self.__on_click_rect_main_color, self.__on_click_rect_top_color = self.__choose_colors()
        self.__event_rect = None
        self.__on_click_rect = None
        self.__flight_details_window = FlightDetailsWindow(flight_id)

        self.setCursor(QtGui.QCursor(Qt.PointingHandCursor))

    def __choose_colors(self):
        if 0 <= self.__duration < 3:
            return (QtGui.QColor(91, 212, 91), QtGui.QColor(109, 237, 109),
                    QtGui.QColor(49, 183, 49), QtGui.QColor(76, 212, 76))

        if 3 <= self.__duration < 5:
            return (QtGui.QColor(230, 202, 90), QtGui.QColor(250, 227, 135),
                    QtGui.QColor(194, 171, 78), QtGui.QColor(209, 184, 82))

        if 5 <= self.__duration < 7:
            return (QtGui.QColor(237, 110, 64), QtGui.QColor(235, 140, 106),
                    QtGui.QColor(191, 88, 65), QtGui.QColor(209, 102, 77))

        if self.__duration >= 7:
            return (QtGui.QColor(217, 85, 85), QtGui.QColor(237, 114, 114),
                    QtGui.QColor(168, 66, 66), QtGui.QColor(191, 88, 88))

    def paintEvent(self, event):
        self.__event_rect = event.rect()

        qp = QtGui.QPainter()
        qp.begin(self)
        self.__draw(qp)
        qp.end()

    def mousePressEvent(self, event):
        self.__on_click_rect = QRect(self.__event_rect)
        self.update()

    def mouseReleaseEvent(self, event):
        self.__on_click_rect = None
        self.update()
        self.__flight_details_window.show()

    def __draw(self, qp):
        coords = self.__event_rect.getCoords()

        qp.setPen(self.__main_color if not self.__on_click_rect else self.__on_click_rect_main_color)
        qp.setBrush(self.__main_color if not self.__on_click_rect else self.__on_click_rect_main_color)
        qp.drawRect(self.__event_rect)

        qp.setPen(self.__top_color if not self.__on_click_rect else self.__on_click_rect_top_color)
        qp.setBrush(self.__top_color if not self.__on_click_rect else self.__on_click_rect_top_color)
        qp.drawRect(coords[0], coords[1], coords[2], 5)

        qp.setPen(QtGui.QColor(0, 0, 0))
        qp.setBrush(QtGui.QColor(0, 0, 0))

        if self.__duration >= 2:
            if self.__duration == 2:
                qp_font = qp.font()
                qp_font.setPixelSize(14)
                qp.setFont(qp_font)

            qp.drawText(self.__event_rect, Qt.AlignCenter, self.__text)
