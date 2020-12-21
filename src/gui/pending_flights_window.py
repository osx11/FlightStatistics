from PyQt5 import QtWidgets as QtW
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from datetime import datetime
from database import FlightStatistics
from settings import Settings
from .flight_details_window import FlightDetailsWindow


class PendingFlightsWindow(QtW.QWidget):
    def __init__(self, parent):
        super().__init__()

        self.__parent = parent
        self.__layout = QtW.QGridLayout()
        self.__progress = QtW.QLabel('Calculating distance: .../...')

        self.setWindowModality(Qt.WindowModality(2))
        self.setFixedSize(480, 300)
        self.setWindowTitle('Pending flights')
        self.setLayout(self.__layout)
        self.setStyleSheet(Settings().style)

    def __show_details(self, flight_id):
        self.__details = FlightDetailsWindow(flight_id)
        self.__details.show()

    def __delete_flight(self, flight_id):
        FlightStatistics.delete_by_id(flight_id)
        self.update_flight_schedule()

    def __open_flight(self, flight_id):
        FlightStatistics.open_flight(flight_id)

        self.__parent.set_status('TRCKNG', 'color_blue')
        self.update_flight_schedule()

    def __close_flight(self):
        def post():
            self.update_flight_schedule()
            self.__parent.set_status('READY')
            self.__parent.render_flights()

        FlightStatistics.close_flight(self.__update_progressbar, post)
        self.__progress.show()

    def __clear_layout(self):
        for i in reversed(range(self.__layout.count())):
            self.__layout.itemAt(i).widget().setParent(None)

    def update_flight_schedule(self):
        self.__clear_layout()

        query = (FlightStatistics
                 .select()
                 .where(FlightStatistics.actual_arrival_time == None)
                 .limit(5)
                 .order_by(FlightStatistics.scheduled_departure_date))

        if query.count() == 0:
            header = QtW.QLabel('There are no pending flights')
        else:
            header = QtW.QLabel('Showing next 5 flights')

        header_font = header.font()
        header_font.setPixelSize(22)
        header.setFont(header_font)
        self.__layout.addWidget(header, 0, 0, 1, 5, Qt.AlignHCenter)

        for pos, flight in enumerate(query):
            details_button = QtW.QPushButton('D', self)
            delete_button = QtW.QPushButton('X', self)

            if FlightStatistics.has_opened_flight():
                if FlightStatistics.get_opened_flight() == flight.id:
                    openclose_button = QtW.QPushButton('C', self)
                    openclose_button.clicked.connect(self.__close_flight)
                else:
                    openclose_button = QtW.QPushButton('O', self)
                    openclose_button.setDisabled(True)
            else:
                openclose_button = QtW.QPushButton('O', self)

                now = datetime.now()
                if now.strftime('%d.%m.%y') != flight.scheduled_departure_date:
                    openclose_button.setDisabled(True)
                else:
                    openclose_button.clicked.connect(lambda checked, flight_id=flight.id: self.__open_flight(flight_id))

            delete_button.setProperty('color', 'color_red')
            delete_button.setCursor(QCursor(Qt.PointingHandCursor))
            details_button.setCursor(QCursor(Qt.PointingHandCursor))
            openclose_button.setCursor(QCursor(Qt.PointingHandCursor))

            details_button.clicked.connect(lambda checked, flight_id=flight.id: self.__show_details(flight_id))
            delete_button.clicked.connect(lambda checked, flight_id=flight.id: self.__delete_flight(flight_id))

            self.__layout.addWidget(QtW.QLabel(flight.scheduled_departure_date), pos+1, 0)
            self.__layout.addWidget(QtW.QLabel(f'{flight.departure_city}-{flight.arrival_city}'), pos+1, 1)
            self.__layout.addWidget(details_button, pos+1, 2)
            self.__layout.addWidget(openclose_button, pos+1, 3)
            self.__layout.addWidget(delete_button, pos+1, 4)

        self.__layout.addWidget(self.__progress, 7, 0, 1, 5)
        self.__progress.hide()

    def __update_progressbar(self, progress):
        self.__progress.setText(progress)

