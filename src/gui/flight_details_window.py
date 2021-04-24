from PyQt5 import QtWidgets as QtW
from PyQt5.QtGui import QCursor, QIntValidator
from PyQt5.QtCore import Qt
from database import FlightStatistics
from settings import Settings
from gui.recorded_flight_window import RecordedFlightWindow


class FlightDetailsWindow(QtW.QWidget):
    def __init__(self, flight_id):
        super().__init__()

        self.__layout = QtW.QGridLayout()
        self.__flight = FlightStatistics.get_by_id(flight_id)

        label_header = QtW.QLabel(f'{self.__flight.flight_number} [{self.__flight.departure_icao}-{self.__flight.arrival_icao}]')
        label_header_font = label_header.font()
        label_header_font.setPixelSize(22)
        label_header.setFont(label_header_font)
        self.__layout.addWidget(label_header, 0, 0, 1, 2, Qt.AlignCenter)

        self.__layout.addWidget(QtW.QLabel('Departure city'), 1, 0)
        self.__layout.addWidget(QtW.QLabel(self.__flight.departure_city), 1, 1)

        self.__layout.addWidget(QtW.QLabel('Arrival city'), 2, 0)
        self.__layout.addWidget(QtW.QLabel(self.__flight.arrival_city), 2, 1)

        self.__layout.addWidget(QtW.QLabel('Departure date'), 3, 0)
        self.__layout.addWidget(QtW.QLabel(self.__flight.scheduled_departure_date), 3, 1)

        self.__layout.addWidget(QtW.QLabel('Scheduled departure time'), 5, 0)
        self.__layout.addWidget(QtW.QLabel(self.__flight.scheduled_departure_time), 5, 1)

        self.__layout.addWidget(QtW.QLabel('Actual departure time'), 6, 0)
        self.__layout.addWidget(QtW.QLabel(self.__flight.actual_departure_time if self.__flight.actual_departure_time else '---'), 6, 1)

        self.__layout.addWidget(QtW.QLabel('Actual arrival date'), 7, 0)
        self.__layout.addWidget(QtW.QLabel(self.__flight.actual_arrival_date if self.__flight.actual_arrival_date else '---'), 7, 1)

        self.__layout.addWidget(QtW.QLabel('Actual arrival time'), 8, 0)
        self.__layout.addWidget(QtW.QLabel(self.__flight.actual_arrival_time if self.__flight.actual_arrival_time else '---'), 8, 1)

        self.__layout.addWidget(QtW.QLabel('Aircraft'), 9, 0)
        self.__layout.addWidget(QtW.QLabel(self.__flight.aircraft), 9, 1)

        distance_km = 0

        if self.__flight.flight_time:
            distance_km = round(self.__flight.distance * 1.85)
            label_flight_time = QtW.QLabel(f'BLOCK: {self.__flight.flight_time}')
            label_flight_time_font = label_flight_time.font()
            label_flight_time_font.setPixelSize(20)
            label_flight_time.setFont(label_flight_time_font)

            self.__label_distance = QtW.QLabel(f'DIST: {self.__flight.distance} NM ({distance_km} KM)')
            label_distance_font = self.__label_distance.font()
            label_distance_font.setPixelSize(20)
            self.__label_distance.setFont(label_distance_font)

            self.__layout.addWidget(label_flight_time, 10, 0, 1, 2, Qt.AlignCenter)
            self.__layout.addWidget(self.__label_distance, 11, 0, 1, 2, Qt.AlignCenter)

        if self.__flight.actual_departure_time and self.__flight.actual_departure_time > self.__flight.scheduled_departure_time:
            hours_diff = int(self.__flight.actual_departure_time[:2]) - int(self.__flight.scheduled_departure_time[:2])
            minutes_diff = int(self.__flight.actual_departure_time[3:]) - int(self.__flight.scheduled_departure_time[3:])

            if hours_diff < 10:
                hours_diff = f'0{hours_diff}'

            if minutes_diff < 10:
                minutes_diff = f'0{minutes_diff}'

            label_delayed = QtW.QLabel(f'With a delay of {hours_diff}:{minutes_diff}')
            label_delayed.setProperty('color', 'color_red')

            self.__layout.addWidget(label_delayed, 12, 0, 1, 2, Qt.AlignCenter)

        if len(self.__flight.flight_points) > 0:
            points = [[], [], []]

            for i, point in enumerate(self.__flight.flight_points):
                points[1].append(point.latitude)
                points[0].append(point.longitude)
                points[2].append(point.altitude)

            self.__rfw = RecordedFlightWindow(points)
            button_show_rfw = QtW.QPushButton('Show recording')
            button_show_rfw.clicked.connect(self.__show_recording)
            button_show_rfw.setCursor(QCursor(Qt.PointingHandCursor))

            self.__layout.addWidget(button_show_rfw, 13, 0, 1, 2)

        if distance_km == 0:
            self.__label_no_distance = QtW.QLabel('No distance in db. Provide it manually')
            self.__label_no_distance.setProperty('color', 'color_red')

            self.__input_distance = QtW.QLineEdit()
            self.__input_distance.setValidator(QIntValidator(bottom=1))
            self.__input_distance.setPlaceholderText('Provide distance in NM')

            self.__button_submit_distance = QtW.QPushButton('Set distance')
            self.__button_submit_distance.clicked.connect(self.__set_distance)
            self.__button_submit_distance.setCursor(QCursor(Qt.PointingHandCursor))

            self.__layout.addWidget(self.__label_no_distance, 13, 0, 1, 2, Qt.AlignCenter)
            self.__layout.addWidget(self.__input_distance, 14, 0)
            self.__layout.addWidget(self.__button_submit_distance, 14, 1)

        self.setWindowModality(Qt.WindowModality(2))
        self.setFixedSize(360, 500)
        self.setWindowTitle('Flight details')
        self.setLayout(self.__layout)
        self.setStyleSheet(Settings().style)
        
    def __set_distance(self):
        if dist := self.__input_distance.text():
            dist = int(dist)
            if dist > 0:
                FlightStatistics.update(distance=dist).where(FlightStatistics.id == self.__flight.id).execute()

                self.__layout.removeWidget(self.__label_no_distance)
                self.__layout.removeWidget(self.__input_distance)
                self.__layout.removeWidget(self.__button_submit_distance)

                self.__label_no_distance = None
                self.__input_distance = None
                self.__button_submit_distance = None

                dist_km = round(dist * 1.85)
                self.__label_distance.setText(f'DIST: {dist} NM ({dist_km} KM)')

    def __show_recording(self):
        self.__rfw.render_recorded_flight_plot()
        self.__rfw.show()
