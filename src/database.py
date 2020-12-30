from peewee import *
from datetime import datetime, time
from time import sleep
from settings import Settings
from utils.measurementutils import DistanceCalculator


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

            try:
                tomorrow = datetime(now.year, now.month, now.day + 1, 0, 0, 0)
            except ValueError:
                if now.month != 12:
                    tomorrow = datetime(now.year, now.month + 1, 1, 0, 0, 0)
                else:
                    tomorrow = datetime(now.year + 1, 1, 1, 0, 0, 0)

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
    def close_flight(cls, progressbar_updater, on_done):
        def post(total_dist):
            (FlightStatistics
             .update(actual_arrival_date=now.strftime('%d.%m.%y'),
                     actual_arrival_time=now.strftime('%H:%M'),
                     flight_time=flight_time.strftime('%H:%M'),
                     distance=total_dist)
             .where(FlightStatistics.id == cls.get_opened_flight())
             .execute())

            delattr(cls, 'opened_flight')

            if on_done:
                on_done()

        now = datetime.now()

        flight = FlightStatistics.get_by_id(cls.get_opened_flight())
        departure_date = flight.scheduled_departure_date
        departure_time = flight.actual_departure_time
        departure_datetime = datetime.strptime(f'{departure_date} {departure_time}', '%d.%m.%y %H:%M')

        flight_time_delta = now - departure_datetime
        flight_time = time(round(flight_time_delta.seconds/3600), round(flight_time_delta.seconds/60) % 60)

        points = FlightStatistics.get_by_id(cls.get_opened_flight()).flight_points
        distance_calculator = DistanceCalculator(points)

        if progressbar_updater:
            distance_calculator.calc_in_progress.connect(progressbar_updater)

        distance_calculator.calc_done.connect(post)
        distance_calculator.start()

    @classmethod
    def get_opened_flight(cls):
        return cls.opened_flight if cls.has_opened_flight() else None

    @classmethod
    def add_point(cls, lat, lon, alt):
        if cls.has_opened_flight():
            FlightPoints.create(flight_id=cls.get_opened_flight(), latitude=lat, longitude=lon, altitude=alt)


class FlightPoints(Model):
    latitude = FloatField()
    longitude = FloatField()
    altitude = FloatField()
    flight_id = ForeignKeyField(FlightStatistics, backref='flight_points', null=True)

    class Meta:
        database = SqliteDatabase(Settings().database_file)

