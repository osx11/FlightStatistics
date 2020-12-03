from peewee import *
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


class FlightPoints(Model):
    coordinates = CharField(max_length=255)
    flight_id = ForeignKeyField(FlightStatistics, related_name='flight_points', null=True)

    class Meta:
        database = SqliteDatabase(Settings().database_file)

