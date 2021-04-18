from PyQt5.QtCore import QThread, pyqtSignal
from math import atan, sin, cos, pi, sqrt, pow


class DistanceCalculator(QThread):
    calc_in_progress = pyqtSignal(str)
    calc_done = pyqtSignal(int)

    def __init__(self, points):
        super().__init__()
        super().setParent(self)

        self.__points = points
        self.__points_count = len(self.__points)

    def run(self):
        total_dist = self.__calculate_total_distance()
        self.calc_done.emit(total_dist)
        self.sleep(50)

    def __calculate_total_distance(self):
        total_dist = 0

        for i in range(1, self.__points_count):
            lat1 = self.__points[i - 1].latitude
            lon1 = self.__points[i - 1].longitude
            lat2 = self.__points[i].latitude
            lon2 = self.__points[i].longitude

            dist = self.__calculate_distance_between_points(lat1, lon1, lat2, lon2)
            total_dist += dist

            self.calc_in_progress.emit(f'{i}/{self.__points_count}')

        return round(total_dist)

    @staticmethod
    def __calculate_distance_between_points(lat1, lon1, lat2, lon2):
        # formula from https://gis-lab.info/qa/great-circles.html

        earth_radius = 3444  # in nautical miles

        rlat1 = lat1 * pi / 180
        rlon1 = lon1 * pi / 180
        rlat2 = lat2 * pi / 180
        rlon2 = lon2 * pi / 180

        dlon = rlon2 - rlon1

        y = (sqrt(pow(cos(rlat2) * sin(dlon), 2) + pow(cos(rlat1) * sin(rlat2) - sin(rlat1) * cos(rlat2) * cos(dlon), 2)))
        x = sin(rlat1) * sin(rlat2) + cos(rlat1) * cos(rlat2) * cos(dlon)

        return atan(y / x) * earth_radius
