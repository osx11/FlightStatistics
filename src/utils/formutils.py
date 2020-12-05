from datetime import datetime, date, time
from PyQt5.QtCore import QDate, QTime


class FormUtils(object):
    def __init__(self, text_fields, date_fields, time_fields):
        super().__init__()

        self.__text_fields = text_fields
        self.__date_fields = date_fields
        self.__time_fields = time_fields

    def _validate_all_fields(self):
        is_ok = True

        for field in self.__text_fields:
            if not field.text():
                self.__set_invalid(field)
                is_ok = False

        for field in self.__date_fields:
            if not self.validate_datetime_field(field, force=True):
                is_ok = False

        return is_ok

    @staticmethod
    def __set_invalid(field):
        field.setProperty('status', 'invalid')
        field.style().polish(field)

    @staticmethod
    def __set_valid(field):
        field.setProperty('status', 'valid')
        field.style().polish(field)

    def _revalidate_field_on_input(self, field):
        prop = field.property('status')
        if prop:
            if field.text():
                self.__set_valid(field)
            else:
                self.__set_invalid(field)

    def validate_datetime_field(self, field, force=False):
        now = datetime.now()
        qdate = field.date()

        prop = field.property('status')

        if prop or force:
            if date(qdate.year(), qdate.month(), qdate.day()) < date(now.year, now.month, now.day):
                self.__set_invalid(field)
                return False

            self.__set_valid(field)
        return True

    def _clear_datetime_inputs(self):
        # since i usually fly on saturdays, calculate the date of the nearest saturday

        now = datetime.now()

        current_weekday = now.weekday()
        remaining_to_saturday = 5 - current_weekday
        remaining_to_saturday_timestamp = 60*60*24*remaining_to_saturday
        saturday = datetime.fromtimestamp(now.timestamp() + remaining_to_saturday_timestamp)

        qdate = QDate(saturday.year, saturday.month, saturday.day)
        qtime = QTime(14, 00, 00)

        for field in self.__date_fields:
            field.setDate(qdate)

        for field in self.__time_fields:
            field.setTime(qtime)

    def _clear_text_inputs(self):
        for item in self.__text_fields:
            item.clear()
            item.setProperty('status', None)
            item.style().polish(item)
