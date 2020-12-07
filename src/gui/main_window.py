from PyQt5 import QtWidgets as QtW
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from .widgets.time_bar_widget import TimeBarWidget
from datetime import datetime
from threading import Thread
from time import sleep
from math import ceil
from settings import Settings
from .new_flight_window import NewFlightWindow
from .pending_flights_window import PendingFlightsWindow
from .flight_details_window import FlightDetailsWindow
from database import FlightStatistics


class MainWindow(QtW.QWidget):
    def __init__(self):
        super().__init__()

        self.__layout = QtW.QGridLayout()

        self.__saved_flights_layout = QtW.QGridLayout()
        self.__group_box = QtW.QGroupBox()

        self.__clock = QtW.QLabel('READY')
        self.__clock.setObjectName('clock')
        self.__layout.addWidget(self.__clock, 0, 0)

        self.__row_count = 0

        for i in range(24):
            self.__layout.addWidget(QtW.QLabel(f'{i}:00'), 0, i+1)

        self.render_flights()

        label_ready = QtW.QLabel('READY')
        label_ready.setObjectName('label_ready')
        self.__layout.addWidget(label_ready, 0, 25)

        self.__group_box.setLayout(self.__saved_flights_layout)
        self.__scroll_area = QtW.QScrollArea()
        self.__scroll_area.setWidget(self.__group_box)
        self.__scroll_area.setWidgetResizable(True)
        self.__scroll_area.setFixedHeight(265)

        self.__layout.addWidget(self.__scroll_area, 1, 0, 1, 26)

        button_new_flight = QtW.QPushButton('New flight', self)
        button_show_pending = QtW.QPushButton('Show pending', self)
        button_stats = QtW.QPushButton('Show total', self)
        # bind
        button_import = QtW.QPushButton('Import', self)
        # bind

        button_new_flight.setCursor(QCursor(Qt.PointingHandCursor))
        button_show_pending.setCursor(QCursor(Qt.PointingHandCursor))
        button_stats.setCursor(QCursor(Qt.PointingHandCursor))
        button_import.setCursor(QCursor(Qt.PointingHandCursor))

        self.__layout.addWidget(button_new_flight, 2, 0, 1, 3)
        self.__layout.addWidget(button_show_pending, 2, 3, 1, 3)
        self.__layout.addWidget(button_stats, 2, 6, 1, 3)
        self.__layout.addWidget(button_import, 2, 9, 1, 3)

        label_copyright = QtW.QLabel('© 2020 osx11')
        label_copyright.setObjectName('label_copyright')
        self.__layout.addWidget(label_copyright, 2, 24, 1, 2)

        Thread(target=self.__update_clock, daemon=True).start()

        self.setWindowTitle('Flight Statistics')
        self.setLayout(self.__layout)
        self.setStyleSheet(Settings().style)
        self.show()

        self.__new_flight_window = NewFlightWindow()
        button_new_flight.clicked.connect(self.__new_flight_window.show)

        self.__pending_flights_window = PendingFlightsWindow(self)
        button_show_pending.clicked.connect(self.__show_pending_flights_window)

    def __clear_saved_flights_layout(self):
        for i in reversed(range(self.__saved_flights_layout.count())):
            self.__saved_flights_layout.itemAt(i).widget().setParent(None)

        # this have to be filled with empty labels otherwise timebars will be displayed incorrectly
        for i in range(25):
            self.__saved_flights_layout.addWidget(QtW.QLabel(''), 0, i)

    def render_flights(self):
        self.__clear_saved_flights_layout()

        query = (FlightStatistics
                 .select()
                 .where(FlightStatistics.actual_arrival_time != None)
                 .order_by(FlightStatistics.scheduled_departure_date))

        self.__row_count = query.count()

        for pos, flight in enumerate(query):
            departure_date = flight.scheduled_departure_date[:5]
            arrival_date = flight.actual_arrival_date[:5]
            actual_departure_hour = int(flight.actual_departure_time[:2])
            actual_arrival_hour = int(flight.actual_arrival_time[:2])
            flight_time = ceil(float(flight.flight_time[:2]) + float(flight.flight_time[-2:])/60)

            arrived_next_day = arrival_date > departure_date

            timebar = TimeBarWidget(f'{flight.departure_icao}-{flight.arrival_icao}', flight_time, flight.id)
            timebar_nextday = TimeBarWidget(f'{flight.departure_icao}-{flight.arrival_icao}', flight_time, flight.id)

            if not arrived_next_day:
                self.__saved_flights_layout.addWidget(QtW.QLabel(departure_date), pos, 0)
                self.__saved_flights_layout.addWidget(timebar, pos, actual_departure_hour, 1, flight_time)
            else:
                self.__saved_flights_layout.addWidget(QtW.QLabel(departure_date), pos, 0)
                self.__saved_flights_layout.addWidget(QtW.QLabel(arrival_date), pos+1, 0)

                self.__saved_flights_layout.addWidget(timebar, pos, actual_departure_hour, 1, (24-actual_departure_hour))
                self.__saved_flights_layout.addWidget(timebar_nextday, pos+1, 1, 1, actual_arrival_hour)

    def __update_clock(self):
        while True:
            now = datetime.now()

            hour = now.hour
            if hour < 10:
                hour = f'0{hour}'

            minute = now.minute
            if minute < 10:
                minute = f'0{minute}'

            remaining = 60 - now.second

            self.__clock.setText(f'{hour}:{minute}Z')
            sleep(remaining)

    def __show_pending_flights_window(self):
        self.__pending_flights_window.update_flight_schedule()
        self.__pending_flights_window.show()
