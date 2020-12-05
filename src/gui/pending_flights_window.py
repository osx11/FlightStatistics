from PyQt5 import QtWidgets as QtW
from PyQt5.QtCore import Qt
from database import FlightStatistics
from settings import Settings
from .flight_details_window import FlightDetailsWindow


class PendingFlightsWindow(QtW.QWidget):
    def __init__(self):
        super().__init__()

        self.__layout = QtW.QGridLayout()

        header = QtW.QLabel('Showing next 5 flights')
        header_font = header.font()
        header_font.setPixelSize(22)
        header.setFont(header_font)
        self.__layout.addWidget(header, 0, 0, 1, 5, Qt.AlignHCenter)

        query = FlightStatistics.select().where(FlightStatistics.actual_arrival_time == None).limit(2)

        for pos, flight in enumerate(query):
            details_button = QtW.QPushButton('D', self)
            open_button = QtW.QPushButton('O', self)
            delete_button = QtW.QPushButton('C', self)

            delete_button.setProperty('status', 'danger')

            details_button.clicked.connect(lambda checked, flight_id=flight.id: self.__show_details(flight_id))

            # todo open_button.clicked.connect() flight will be opened from FlightStatistics class directly
            delete_button.clicked.connect(lambda checked, flight_id=flight.id: self.__delete_flight(flight_id))

            self.__layout.addWidget(QtW.QLabel(flight.scheduled_departure_date), pos+1, 0)
            self.__layout.addWidget(QtW.QLabel(f'{flight.departure_city}-{flight.arrival_city}'), pos+1, 1)
            self.__layout.addWidget(details_button, pos+1, 2)
            self.__layout.addWidget(open_button, pos+1, 3)
            self.__layout.addWidget(delete_button, pos+1, 4)

        self.setWindowModality(Qt.WindowModality(2))
        self.setFixedSize(480, 300)
        self.setWindowTitle('Pending flights')
        self.setLayout(self.__layout)
        self.setStyleSheet(Settings().style)

    def __show_details(self, flight_id):
        self.__details = FlightDetailsWindow(flight_id)
        self.__details.show()

    def __delete_flight(self, flight_id):
        pass

    def __update_flight_schedule(self):
        # todo
        # this will be needed because now if you open pending window after adding a new flights,
        # there will be no changes
        pass
