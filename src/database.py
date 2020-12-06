from peewee import *
from datetime import datetime, time
from settings import Settings


def create_tables():
    with SqliteDatabase(Settings().database_file) as connected_db:
        connected_db.create_tables([FlightStatistics, FlightPoints])


class FlightStatistics(Model):
    flight_number = CharField(max_length=10)
    scheduled_departure_date = DateField(formats='DD.MM.YYYY')
    scheduled_departure_time = TimeField(formats='HH:MM')
    actual_arrival_date = DateField(formats='DD.MM.YYYY', null=True)
    actual_departure_time = TimeField(formats='HH:MM', null=True)
    actual_arrival_time = TimeField(formats='HH:MM', null=True)
    aircraft = CharField(max_length=10)
    departure_icao = CharField(max_length=4)
    arrival_icao = CharField(max_length=4)
    departure_city = CharField(max_length=255)
    arrival_city = CharField(max_length=255)
    flight_time = TimeField(formats='HH:MM', null=True)

    class Meta:
        database = SqliteDatabase(Settings().database_file)

    @classmethod
    def has_opened_flight(cls):
        return hasattr(cls, 'opened_flight')

    @classmethod
    def open_flight(cls, flight_id):
        assert not cls.has_opened_flight()
        cls.opened_flight = flight_id

        now = datetime.now()
        (FlightStatistics
         .update(actual_departure_time=now.strftime('%H:%M'))
         .where(FlightStatistics.id == flight_id)
         .execute())

    @classmethod
    def close_flight(cls):
        now = datetime.now()

        flight = FlightStatistics.get_by_id(cls.get_opened_flight())
        departure_date = flight.scheduled_departure_date
        departure_time = flight.actual_departure_time

        departure_datetime = datetime(int(departure_date[-4:]),
                                      int(departure_date[3:5]),
                                      int(departure_date[:2]),
                                      int(departure_time[:2]),
                                      int(departure_time[-2:]))
        flight_time_delta = now - departure_datetime
        flight_time = time(flight_time_delta.seconds//3660, (flight_time_delta.seconds//60) % 60)

        (FlightStatistics
         .update(actual_arrival_date=now.strftime('%d.%m.%y'),
                 actual_arrival_time=now.strftime('%H:%M'),
                 flight_time=flight_time.strftime('%H:%M'))
         .where(FlightStatistics.id == cls.get_opened_flight())
         .execute())

        delattr(cls, 'opened_flight')

    @classmethod
    def get_opened_flight(cls):
        return cls.opened_flight if cls.has_opened_flight() else None

    @classmethod
    def add_point(cls, lat, lon):
        print('got lat lon ', cls.has_opened_flight())
        if cls.has_opened_flight():
            print('set!')
            FlightPoints.create(flight_id=cls.get_opened_flight(), latitude=lat, longitude=lon)


class FlightPoints(Model):
    latitude = FloatField()
    longitude = FloatField()
    flight_id = ForeignKeyField(FlightStatistics, backref='flight_points', null=True)

    class Meta:
        database = SqliteDatabase(Settings().database_file)

