from datetime import datetime
from PyQt5.QtCore import QDate, QTime


class FormUtils(object):
    def __init__(self, text_fields, date_fields, time_fields):
        super().__init__()

        self.__text_fields = text_fields
        self.__date_fields = date_fields
        self.__time_fields = time_fields

    def _validate_fields(self):
        is_ok = True

        for field in self.__text_fields:
            if not field.text():
                field.setProperty('status', 'invalid')
                field.style().polish(field)
                is_ok = False

        return is_ok

    @staticmethod
    def _revalidate_field_on_input(field):
        prop = field.property('status')
        if prop:
            if field.text():
                field.setProperty('status', 'valid')
            else:
                field.setProperty('status', 'invalid')

            if prop != field.property('status'):
                field.style().polish(field)

    def _clear_datetime_inputs(self):
        # since i usually fly on saturdays, calculate the date of the nearest saturday

        now = datetime.now()

        current_weekday = now.weekday()
        remaining_to_saturday = 5 - current_weekday
        remaining_to_saturday_timestamp = 60*60*24*remaining_to_saturday
        saturday = datetime.fromtimestamp(now.timestamp() + remaining_to_saturday_timestamp)

        date = QDate(saturday.year, saturday.month, saturday.day)
        time = QTime(14, 00, 00)

        for field in self.__date_fields:
            field.setDate(date)

        for field in self.__time_fields:
            field.setTime(time)

    def _clear_text_inputs(self):
        for item in self.__text_fields:
            item.clear()
            item.setProperty('status', None)
            item.style().polish(item)
