from PyQt5 import QtWidgets as QtW
from PyQt5.QtCore import Qt
from database import FlightStatistics
from settings import Settings


class FlightDetailsWindow(QtW.QWidget):
    def __init__(self, flight_id):
        super().__init__()

        self.__layout = QtW.QGridLayout()
        flight = FlightStatistics.get_by_id(flight_id)

        header_label = QtW.QLabel(f'{flight.flight_number} [{flight.departure_icao}-{flight.arrival_icao}]')
        header_label_font = header_label.font()
        header_label_font.setPixelSize(22)
        header_label.setFont(header_label_font)
        self.__layout.addWidget(header_label, 0, 0, 1, 2, Qt.AlignCenter)

        self.__layout.addWidget(QtW.QLabel('Departure city'), 1, 0)
        self.__layout.addWidget(QtW.QLabel(flight.departure_city), 1, 1)

        self.__layout.addWidget(QtW.QLabel('Arrival city'), 2, 0)
        self.__layout.addWidget(QtW.QLabel(flight.arrival_city), 2, 1)

        self.__layout.addWidget(QtW.QLabel('Scheduled departure date'), 3, 0)
        self.__layout.addWidget(QtW.QLabel(flight.scheduled_departure_date), 3, 1)

        self.__layout.addWidget(QtW.QLabel('Scheduled departure time'), 5, 0)
        self.__layout.addWidget(QtW.QLabel(flight.scheduled_departure_time), 5, 1)

        self.__layout.addWidget(QtW.QLabel('Actual departure time'), 6, 0)
        self.__layout.addWidget(QtW.QLabel(flight.actual_departure_time if flight.actual_departure_time else '---'), 6, 1)

        self.__layout.addWidget(QtW.QLabel('Actual arrival date'), 7, 0)
        self.__layout.addWidget(QtW.QLabel(flight.actual_arrival_date if flight.actual_arrival_date else '---'), 7, 1)

        self.__layout.addWidget(QtW.QLabel('Actual arrival time'), 8, 0)
        self.__layout.addWidget(QtW.QLabel(flight.actual_arrival_time if flight.actual_arrival_time else '---'), 8, 1)

        self.__layout.addWidget(QtW.QLabel('Aircraft'), 9, 0)
        self.__layout.addWidget(QtW.QLabel(flight.aircraft), 9, 1)

        if flight.flight_time:
            flight_time_label = QtW.QLabel(f'BLOCK: {flight.flight_time}')
            flight_time_label_font = flight_time_label.font()
            flight_time_label_font.setPixelSize(20)
            flight_time_label.setFont(flight_time_label_font)
            self.__layout.addWidget(flight_time_label, 10, 0, 1, 2, Qt.AlignCenter)

        if flight.actual_departure_time and flight.actual_departure_time > flight.scheduled_departure_time:
            hours_diff = int(flight.actual_departure_time[:2]) - int(flight.scheduled_departure_time[:2])
            minutes_diff = int(flight.actual_departure_time[3:]) - int(flight.scheduled_departure_time[3:])
            delayed_label = QtW.QLabel(f'With a delay of {hours_diff}:{minutes_diff}')
            delayed_label.setProperty('color', 'color_red')

            self.__layout.addWidget(delayed_label, 11, 0, 1, 2, Qt.AlignCenter)

        self.setWindowModality(Qt.WindowModality(2))
        self.setFixedSize(360, 300)
        self.setWindowTitle('Flight details')
        self.setLayout(self.__layout)
        self.setStyleSheet(Settings().style)
