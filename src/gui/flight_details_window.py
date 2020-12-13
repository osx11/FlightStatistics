from PyQt5 import QtWidgets as QtW
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from database import FlightStatistics
from settings import Settings
from gui.recorded_flight_window import RecordedFlightWindow


class FlightDetailsWindow(QtW.QWidget):
    def __init__(self, flight_id):
        super().__init__()

        self.__layout = QtW.QGridLayout()
        flight = FlightStatistics.get_by_id(flight_id)

        label_header = QtW.QLabel(f'{flight.flight_number} [{flight.departure_icao}-{flight.arrival_icao}]')
        label_header_font = label_header.font()
        label_header_font.setPixelSize(22)
        label_header.setFont(label_header_font)
        self.__layout.addWidget(label_header, 0, 0, 1, 2, Qt.AlignCenter)

        self.__layout.addWidget(QtW.QLabel('Departure city'), 1, 0)
        self.__layout.addWidget(QtW.QLabel(flight.departure_city), 1, 1)

        self.__layout.addWidget(QtW.QLabel('Arrival city'), 2, 0)
        self.__layout.addWidget(QtW.QLabel(flight.arrival_city), 2, 1)

        self.__layout.addWidget(QtW.QLabel('Departure date'), 3, 0)
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
            distance_km = round(flight.distance * 1.85)
            label_flight_time = QtW.QLabel(f'BLOCK: {flight.flight_time}')
            label_flight_time_font = label_flight_time.font()
            label_flight_time_font.setPixelSize(20)
            label_flight_time.setFont(label_flight_time_font)

            label_distance = QtW.QLabel(f'DIST: {flight.distance} NM ({distance_km} KM)')
            label_distance_font = label_distance.font()
            label_distance_font.setPixelSize(20)
            label_distance.setFont(label_distance_font)

            self.__layout.addWidget(label_flight_time, 10, 0, 1, 2, Qt.AlignCenter)
            self.__layout.addWidget(label_distance, 11, 0, 1, 2, Qt.AlignCenter)

        if flight.actual_departure_time and flight.actual_departure_time > flight.scheduled_departure_time:
            hours_diff = int(flight.actual_departure_time[:2]) - int(flight.scheduled_departure_time[:2])
            minutes_diff = int(flight.actual_departure_time[3:]) - int(flight.scheduled_departure_time[3:])

            if hours_diff < 10:
                hours_diff = f'0{hours_diff}'

            if minutes_diff < 10:
                minutes_diff = f'0{minutes_diff}'

            delayed_label = QtW.QLabel(f'With a delay of {hours_diff}:{minutes_diff}')
            delayed_label.setProperty('color', 'color_red')

            self.__layout.addWidget(delayed_label, 12, 0, 1, 2, Qt.AlignCenter)

        if len(flight.flight_points) > 0:
            points = [[], [], []]

            for i, point in enumerate(flight.flight_points):
                points[1].append(point.latitude)
                points[0].append(point.longitude)
                points[2].append(point.altitude)

            self.__rfw = RecordedFlightWindow(points)
            button_show_rfw = QtW.QPushButton('Show recording')
            button_show_rfw.clicked.connect(self.__show_recording)
            button_show_rfw.setCursor(QCursor(Qt.PointingHandCursor))

            self.__layout.addWidget(button_show_rfw, 13, 0, 1, 2)

        self.setWindowModality(Qt.WindowModality(2))
        self.setFixedSize(360, 440)
        self.setWindowTitle('Flight details')
        self.setLayout(self.__layout)
        self.setStyleSheet(Settings().style)

    def __show_recording(self):
        self.__rfw.render_recorded_flight_plot()
        self.__rfw.show()
