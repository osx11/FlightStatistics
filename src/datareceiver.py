from pydantic import BaseModel
from socket import *
from struct import unpack
from database import FlightStatistics


class Point(BaseModel):
    latitude: float = 0.0
    longitude: float = 0.0


class DataReceiver:
    def __init__(self, addr, port):
        self.__addr = addr
        self.__port = port
        self.__socket = socket(AF_INET, SOCK_DGRAM)
        self.__socket.bind((addr, port))

    def run(self):
        while True:
            data, _ = self.__socket.recvfrom(1024)
            lat = unpack('f', data[9:13])
            lon = unpack('f', data[13:17])

            FlightStatistics.add_point(lat, lon)
