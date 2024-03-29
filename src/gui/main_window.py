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
from .close_confirmation_window import CloseConfirmationWindow
from .total_stats_window import TotalStatsWindow
from database import FlightStatistics
from openpyxl import load_workbook


class MainWindow(QtW.QWidget):
    def __init__(self):
        super().__init__()

        self.__layout = QtW.QGridLayout()

        self.__saved_flights_layout = QtW.QGridLayout()
        self.__group_box = QtW.QGroupBox()

        self.__clock = QtW.QLabel('00:00')
        self.__clock.setProperty('color', 'color_vlight')
        self.__layout.addWidget(self.__clock, 0, 0)

        self.__row_count = 0

        for i in range(24):
            self.__layout.addWidget(QtW.QLabel(f'{i}:00'), 0, i+1)

        self.render_flights()

        self.__label_status = QtW.QLabel('READY')
        self.__label_status.setProperty('color', 'color_green')
        self.__layout.addWidget(self.__label_status, 0, 25)

        self.__group_box.setLayout(self.__saved_flights_layout)
        self.__scroll_area = QtW.QScrollArea()
        self.__scroll_area.setWidget(self.__group_box)
        self.__scroll_area.setWidgetResizable(True)
        self.__scroll_area.setFixedHeight(400)

        self.__layout.addWidget(self.__scroll_area, 1, 0, 1, 26)

        button_new_flight = QtW.QPushButton('New flight', self)
        button_show_pending = QtW.QPushButton('Show pending', self)
        button_stats = QtW.QPushButton('Show total', self)
        button_import = QtW.QPushButton('Import', self)
        button_import.pressed.connect(self.__import_data)

        button_new_flight.setCursor(QCursor(Qt.PointingHandCursor))
        button_show_pending.setCursor(QCursor(Qt.PointingHandCursor))
        button_stats.setCursor(QCursor(Qt.PointingHandCursor))
        button_import.setCursor(QCursor(Qt.PointingHandCursor))

        self.__layout.addWidget(button_new_flight, 2, 0, 1, 3)
        self.__layout.addWidget(button_show_pending, 2, 3, 1, 3)
        self.__layout.addWidget(button_stats, 2, 6, 1, 3)
        self.__layout.addWidget(button_import, 2, 9, 1, 3)

        label_copyright = QtW.QLabel(f'© {datetime.now().year} osx11')
        label_copyright.setProperty('color', 'color_vlight')
        self.__layout.addWidget(label_copyright, 2, 24, 1, 2)

        Thread(target=self.__update_clock, daemon=True).start()

        self.__new_flight_window = NewFlightWindow()
        button_new_flight.clicked.connect(self.__new_flight_window.show)

        self.__pending_flights_window = PendingFlightsWindow(self)
        button_show_pending.clicked.connect(self.__show_pending_flights_window)

        self.__total_stats_window = TotalStatsWindow()
        button_stats.clicked.connect(self.__show_total_stats_window)

        self.__close_confirmation_window = CloseConfirmationWindow(self)

        self.setFixedSize(1300, 505)
        self.setWindowTitle('Flight Statistics')
        self.setLayout(self.__layout)
        self.setStyleSheet(Settings().style)
        self.show()

    def set_status(self, status, color='color_green'):
        self.__label_status.setText(status)
        self.__label_status.setProperty('color', color)
        self.__label_status.style().polish(self.__label_status)

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
                 .where(FlightStatistics.actual_arrival_time != None))

        self.__row_count = query.count()

        previous_pos_was_nextday = False
        pos = 0

        for flight in query:
            departure_date = flight.scheduled_departure_date[:5]
            arrival_date = flight.actual_arrival_date[:5]
            actual_departure_hour = int(flight.actual_departure_time[:2])
            actual_arrival_hour = int(flight.actual_arrival_time[:2])
            flight_time = ceil(float(flight.flight_time[:2]) + float(flight.flight_time[-2:])/60)

            if actual_departure_hour == 0:
                actual_departure_hour = 1

            if actual_arrival_hour == 0:
                actual_arrival_hour += 1

            if flight_time == 0:
                flight_time = 1

            arrived_next_day = arrival_date > departure_date

            no_distance = flight.distance == 0

            timebar = TimeBarWidget(self,
                                    f'{flight.departure_icao}-{flight.arrival_icao}',
                                    flight_time,
                                    flight.id,
                                    no_distance=no_distance)

            timebar_nextday = TimeBarWidget(self,
                                            f'{flight.departure_icao}-{flight.arrival_icao}',
                                            flight_time, flight.id,
                                            is_next_day=True)

            if not arrived_next_day:
                if previous_pos_was_nextday:
                    pos += 1
                    previous_pos_was_nextday = False
                self.__saved_flights_layout.addWidget(QtW.QLabel(departure_date), pos, 0)
                self.__saved_flights_layout.addWidget(timebar, pos, actual_departure_hour, 1, flight_time)
            else:
                previous_pos_was_nextday = True
                self.__saved_flights_layout.addWidget(QtW.QLabel(departure_date), pos, 0)
                self.__saved_flights_layout.addWidget(QtW.QLabel(arrival_date), pos+1, 0)

                self.__saved_flights_layout.addWidget(timebar, pos, actual_departure_hour, 1, (24-actual_departure_hour))
                self.__saved_flights_layout.addWidget(timebar_nextday, pos+1, 1, 1, actual_arrival_hour)

            pos += 1

    def __update_clock(self):
        while True:
            now = datetime.utcnow()

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

    def __show_total_stats_window(self):
        self.__total_stats_window.update_statistics()
        self.__total_stats_window.show()

    def __import_data(self):
        file_url = QtW.QFileDialog().getOpenFileName()[0]

        if not file_url:
            return

        workbook = load_workbook(file_url)
        sheet = workbook.active

        i = 6
        while dep_city := sheet[f'A{i}'].value:
            dep_icao = sheet[f'B{i}'].value
            dep_dt = sheet[f'C{i}'].value
            arr_city = sheet[f'D{i}'].value
            arr_icao = sheet[f'E{i}'].value
            arr_dt = sheet[F'F{i}'].value
            aircraft = sheet[f'H{i}'].value
            dist = sheet[f'I{i}'].value
            flight_time = sheet[f'L{i}'].value

            FlightStatistics.create(flight_number='OSX11',
                                    scheduled_departure_date=dep_dt.strftime('%d.%m.%y'),
                                    scheduled_departure_time=dep_dt.strftime('%H:%M'),
                                    actual_arrival_date=arr_dt.strftime('%d.%m.%y'),
                                    actual_departure_time=dep_dt.strftime('%H:%M'),
                                    actual_arrival_time=arr_dt.strftime('%H:%M'),
                                    aircraft=aircraft,
                                    departure_icao=dep_icao,
                                    arrival_icao=arr_icao,
                                    departure_city=dep_city,
                                    arrival_city=arr_city,
                                    flight_time=flight_time.strftime('%H:%M'),
                                    distance=dist)

            i += 1

        self.render_flights()

    def closeEvent(self, event):
        if FlightStatistics.has_opened_flight():
            self.__close_confirmation_window.show()
            event.ignore()
