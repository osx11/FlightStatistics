from peewee import *
from datetime import datetime, time
from time import sleep
from math import atan, sin, cos, pi, sqrt, pow
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
    distance = IntegerField(null=True)

    class Meta:
        database = SqliteDatabase(Settings().database_file)

    @staticmethod
    def delete_old_scheduled_flights(schedule_next=False):
        # !NOT FOR RUNNING IN MAIN THREAD IF schedule_next == True!

        now = datetime.now()

        query = (FlightStatistics
                 .select()
                 .where(FlightStatistics.scheduled_departure_date < now.strftime('%d.%m.%y'))
                 .where(FlightStatistics.flight_time == None))

        for flight in query:
            FlightStatistics.delete_by_id(flight.id)

        if schedule_next:
            now = datetime.now()
            tomorrow = datetime(now.year, now.month, now.day + 1, 0, 0, 0)
            diff = tomorrow - now

            sleep(diff.seconds)

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

        departure_datetime = datetime(int(departure_date[-2:]),
                                      int(departure_date[3:5]),
                                      int(departure_date[:2]),
                                      int(departure_time[:2]),
                                      int(departure_time[-2:]))
        flight_time_delta = now - departure_datetime
        flight_time = time(flight_time_delta.seconds//3660, (flight_time_delta.seconds//60) % 60)
        total_dist = cls.calculate_total_distance(cls.get_opened_flight())

        (FlightStatistics
         .update(actual_arrival_date=now.strftime('%d.%m.%y'),
                 actual_arrival_time=now.strftime('%H:%M'),
                 flight_time=flight_time.strftime('%H:%M'),
                 distance=total_dist)
         .where(FlightStatistics.id == cls.get_opened_flight())
         .execute())

        delattr(cls, 'opened_flight')

    @classmethod
    def get_opened_flight(cls):
        return cls.opened_flight if cls.has_opened_flight() else None

    @classmethod
    def add_point(cls, lat, lon, alt):
        if cls.has_opened_flight():
            FlightPoints.create(flight_id=cls.get_opened_flight(), latitude=lat, longitude=lon, altitude=alt)

    @staticmethod
    def calculate_total_distance(flight_id):
        flight = FlightStatistics.get_by_id(flight_id)
        total_dist = 0

        for i in range(1, len(flight.flight_points)):
            lat1 = flight.flight_points[i-1].latitude
            lon1 = flight.flight_points[i-1].longitude
            lat2 = flight.flight_points[i].latitude
            lon2 = flight.flight_points[i].longitude

            dist = FlightStatistics.calculate_distance_between_points(lat1, lon1, lat2, lon2)
            total_dist += dist

        return round(total_dist)

    @staticmethod
    def calculate_distance_between_points(lat1, lon1, lat2, lon2):
        earth_radius = 3444  # in nautical miles

        rlat1 = lat1 * pi / 180
        rlon1 = lon1 * pi / 180
        rlat2 = lat2 * pi / 180
        rlon2 = lon2 * pi / 180

        dlon = rlon2 - rlon1

        y = (sqrt(pow(cos(rlat2) * sin(dlon), 2) + pow(cos(rlat1) * sin(rlat2) - sin(rlat1) * cos(rlat2) * cos(dlon), 2)))
        x = sin(rlat1) * sin(rlat2) + cos(rlat1) * cos(rlat2) * cos(dlon)

        return atan(y / x) * earth_radius


class FlightPoints(Model):
    latitude = FloatField()
    longitude = FloatField()
    altitude = FloatField()
    flight_id = ForeignKeyField(FlightStatistics, backref='flight_points', null=True)

    class Meta:
        database = SqliteDatabase(Settings().database_file)

