from PyQt5 import QtWidgets as QtW
from PyQt5.QtCore import Qt
from peewee import fn
from database import FlightStatistics
from settings import Settings


class TotalStatsWindow(QtW.QWidget):
    def __init__(self):
        super().__init__()
        self.__layout = QtW.QGridLayout()

        self.__input_airport_check = QtW.QLineEdit()
        self.__input_airport_check.setPlaceholderText('ICAO/City')
        self.__label_airport_check = QtW.QLabel('')

        self.__input_airport_check.textEdited.connect(self.__check_airport)

        self.__layout.addWidget(QtW.QLabel('Total distance:'), 0, 0)
        self.__layout.addWidget(QtW.QLabel('Total time:'), 1, 0)
        self.__layout.addWidget(QtW.QLabel('Total airports:'), 2, 0)
        self.__layout.addWidget(QtW.QLabel('Total aircraft:'), 3, 0)
        self.__layout.addWidget(QtW.QLabel('Have I flown to'), 4, 0)
        self.__layout.addWidget(self.__input_airport_check, 4, 1)
        self.__layout.addWidget(self.__label_airport_check, 5, 1)

        self.setWindowModality(Qt.WindowModality(2))
        self.setFixedSize(370, 300)
        self.setWindowTitle('Total statistics')
        self.setLayout(self.__layout)
        self.setStyleSheet(Settings().style)

    def update_statistics(self):
        query_total_dist = FlightStatistics.select(fn.SUM(FlightStatistics.distance).alias('sum'))
        total_dist = query_total_dist[0].sum
        self.__layout.addWidget(QtW.QLabel(f'{total_dist} NM ({int(total_dist*1.85)} KM)'), 0, 1)

        total_time = 0.0
        query_total_time = FlightStatistics.select(FlightStatistics.flight_time)

        for i in query_total_time:
            if not i.flight_time:
                continue

            flight_time = i.flight_time
            total_time += int(flight_time[:2]) + int(flight_time[-2:])/60

        total_time_hours = int(total_time)
        total_time_minutes = int((total_time - total_time_hours) * 60)

        if total_time_hours < 10:
            total_time_hours = f'0{total_time_hours}'

        if total_time_minutes < 10:
            total_time_minutes = f'0{total_time_minutes}'

        self.__layout.addWidget(QtW.QLabel(f'{total_time_hours}:{total_time_minutes}'), 1, 1)

        query_departures = FlightStatistics.select(FlightStatistics.departure_city.alias('airport')).distinct()
        query_arrivals = FlightStatistics.select(FlightStatistics.arrival_city.alias('airport')).distinct()
        query_total_airports = query_departures.union(query_arrivals)
        self.__layout.addWidget(QtW.QLabel(str(len(query_total_airports))), 2, 1)

        query_total_aircraft = FlightStatistics.select(FlightStatistics.aircraft).distinct()
        self.__layout.addWidget(QtW.QLabel(str(len(query_total_aircraft))), 3, 1)

    def __check_airport(self):
        input_text = self.__input_airport_check.text()

        if not input_text:
            self.__label_airport_check.setText('')
            return

        query_departures = (FlightStatistics
                            .select(fn.COUNT().alias('count'))
                            .where((FlightStatistics.departure_city == input_text.title()) | (FlightStatistics.departure_icao == input_text.upper())))

        query_arrivals = (FlightStatistics
                          .select(fn.COUNT().alias('count'))
                          .where((FlightStatistics.arrival_city == input_text.title()) | (FlightStatistics.arrival_icao == input_text.upper())))

        total = query_departures[0].count + query_arrivals[0].count

        if total == 0:
            self.__label_airport_check.setText('No')
            self.__label_airport_check.setProperty('color', 'color_red')
        else:
            self.__label_airport_check.setText(f'Yes, {total} time(s)')
            self.__label_airport_check.setProperty('color', 'color_green')

        self.__label_airport_check.style().polish(self.__label_airport_check)
