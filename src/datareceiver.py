from socket import *
from struct import unpack
from database import FlightStatistics


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
            alt = unpack('f', data[29:33])

            FlightStatistics.add_point(lat[0], lon[0], alt[0])
