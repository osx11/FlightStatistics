from PyQt5 import QtWidgets as QtW
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
import requests
import json
from settings import Settings
from database import FlightStatistics
from utils.formutils import FormUtils


class NewFlightWindow(FormUtils, QtW.QWidget):
    def __init__(self):
        self.__needs_validation = []
        self.__layout = QtW.QGridLayout()

        label_flight = QtW.QLabel('Fl#')
        self.__input_flight = QtW.QLineEdit()
        self.__input_flight.setPlaceholderText('Your flight number')
        self.__input_flight.textEdited.connect(lambda: self.__revalidate_field_on_input(self.__input_flight))
        self.__input_flight.editingFinished.connect(lambda: self.__input_flight.setText(self.__input_flight.text().upper()))
        self.__needs_validation.append(self.__input_flight)

        label_date = QtW.QLabel('Scheduled date')
        self.__input_date = QtW.QDateEdit()
        self.__input_date.setButtonSymbols(QtW.QAbstractSpinBox.NoButtons)
        self.__input_date.dateChanged.connect(lambda: self.__revalidate_datetime_field(self.__input_date))

        label_time = QtW.QLabel('And time')
        self.__input_time = QtW.QTimeEdit()
        self.__input_time.setButtonSymbols(QtW.QAbstractSpinBox.NoButtons)

        label_aircraft = QtW.QLabel('Aircraft')
        self.__input_aircraft = QtW.QLineEdit()
        self.__input_aircraft.setPlaceholderText('Your favorite one')
        self.__input_aircraft.textEdited.connect(lambda: self.__revalidate_field_on_input(self.__input_aircraft))
        self.__needs_validation.append(self.__input_aircraft)

        label_departure_icao = QtW.QLabel('Departure')
        self.__input_departure_icao = QtW.QLineEdit()
        self.__input_departure_icao.setPlaceholderText('ICAO of departure')
        self.__input_departure_icao.textEdited.connect(lambda: self.__revalidate_field_on_input(self.__input_departure_icao))
        self.__input_departure_icao.editingFinished.connect(lambda: self.__handle_icao_input(self.__input_departure_icao, self.__input_departure_city))
        self.__needs_validation.append(self.__input_departure_icao)

        label_arrival_icao = QtW.QLabel('Arrival')
        self.__input_arrival_icao = QtW.QLineEdit()
        self.__input_arrival_icao.setPlaceholderText('ICAO of arrival')
        self.__input_arrival_icao.textEdited.connect(lambda: self.__revalidate_field_on_input(self.__input_arrival_icao))
        self.__input_arrival_icao.editingFinished.connect(lambda: self.__handle_icao_input(self.__input_arrival_icao, self.__input_arrival_city))
        self.__needs_validation.append(self.__input_arrival_icao)

        self.__input_departure_city = QtW.QLineEdit()
        self.__input_departure_city.setPlaceholderText('Name of dep city')
        self.__input_departure_city.textEdited.connect(lambda: self.__revalidate_field_on_input(self.__input_departure_city))
        self.__needs_validation.append(self.__input_departure_city)

        self.__input_arrival_city = QtW.QLineEdit()
        self.__input_arrival_city.setPlaceholderText('Name of arr city')
        self.__input_arrival_city.textEdited.connect(lambda: self.__revalidate_field_on_input(self.__input_arrival_city))
        self.__needs_validation.append(self.__input_arrival_city)

        super().__init__(self.__needs_validation, [self.__input_date], [self.__input_time])

        button_submit = QtW.QPushButton('Confirm', self)
        button_submit.setCursor(QCursor(Qt.PointingHandCursor))
        button_submit.clicked.connect(self.__submit)

        self.__layout.addWidget(label_flight, 0, 0)
        self.__layout.addWidget(self.__input_flight, 0, 1, 1, 3)

        self.__layout.addWidget(label_date, 1, 0)
        self.__layout.addWidget(self.__input_date, 1, 1)

        self.__layout.addWidget(label_time, 1, 2)
        self.__layout.addWidget(self.__input_time, 1, 3)

        self.__layout.addWidget(label_aircraft, 2, 0)
        self.__layout.addWidget(self.__input_aircraft, 2, 1)

        self.__layout.addWidget(label_departure_icao, 3, 0)
        self.__layout.addWidget(self.__input_departure_icao, 3, 1)

        self.__layout.addWidget(label_arrival_icao, 3, 2)
        self.__layout.addWidget(self.__input_arrival_icao, 3, 3)

        self.__layout.addWidget(QtW.QLabel('City'), 4, 0)
        self.__layout.addWidget(self.__input_departure_city, 4, 1)

        self.__layout.addWidget(QtW.QLabel('City'), 4, 2)
        self.__layout.addWidget(self.__input_arrival_city, 4, 3)

        self.__layout.addWidget(button_submit, 5, 0, 1, 4)

        self.__label_status = QtW.QLabel('Status after submit')
        self.__layout.addWidget(self.__label_status, 6, 0, 1, 4)
        self.__label_status.hide()

        super()._clear_datetime_inputs()
        self.setWindowModality(Qt.WindowModality(2))
        self.setWindowTitle('Register a new flight')
        self.setLayout(self.__layout)
        self.setStyleSheet(Settings().style)

    def __revalidate_field_on_input(self, field):
        super()._revalidate_field_on_input(field)

    def __revalidate_datetime_field(self, field):
        super().validate_datetime_field(field)

    def __handle_icao_input(self, icao_field, city_field):
        icao_field.setText(icao_field.text().upper())
        super()._revalidate_field_on_input(city_field)

        response = requests.post('https://openflights.org/php/apsearch.php', data={'icao': icao_field.text()})
        if response.status_code != 200:
            city_field.setText(f'POST code: {response.status_code}')
            return

        data = json.loads(response.content.decode('utf-8'))
        if 'airports' not in data:
            city_field.setText('Fetching failed')
            return

        city_name = data['airports'][0]['city']
        city_field.setText(city_name)

    def __submit(self):
        self.__label_status.hide()
        validation_result = super()._validate_all_fields()

        if not validation_result:
            self.__set_status('Something\'s wrong! Check fields.', is_error=True)
            return

        formatted_date = self.__input_date.text()
        formatted_date = formatted_date[:6] + formatted_date[-2:]

        FlightStatistics.create(flight_number=self.__input_flight.text(),
                                scheduled_departure_date=formatted_date,
                                scheduled_departure_time=self.__input_time.text(),
                                aircraft=self.__input_aircraft.text(),
                                departure_icao=self.__input_departure_icao.text(),
                                arrival_icao=self.__input_arrival_icao.text(),
                                departure_city=self.__input_departure_city.text(),
                                arrival_city=self.__input_arrival_city.text())

        super()._clear_datetime_inputs()
        super()._clear_text_inputs()

        self.__set_status('It\'s ok! Prepare carefully ;)')

    def __set_status(self, status, is_error=False):
        self.__label_status.setText(status)

        if is_error:
            self.__label_status.setProperty('color', 'color_red')
        else:
            self.__label_status.setProperty('color', 'color_green')

        self.__label_status.style().polish(self.__label_status)
        self.__label_status.show()

    def closeEvent(self, event):
        super()._clear_text_inputs()
        super()._clear_datetime_inputs()
        self.__label_status.hide()
