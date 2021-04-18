from PyQt5 import QtWidgets as QtW
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from shapefile import Reader
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backend_bases import MouseButton
import matplotlib.pyplot as plt
from settings import Settings
from utils.plotutils import PlotUtils


class RecordedFlightWindow(QtW.QWidget):
    def __init__(self, flight_points):
        super().__init__()
        self.__flight_points = flight_points
        self.__constraint = None

        self.__fig, self.__ax = plt.subplots()
        self.__canvas = None
        self.__zoom_start_point = None
        self.__rendered_cities = []

        self.__fig.set_facecolor('#2f3640')
        self.__ax.set_facecolor('#2f3640')
        self.__ax.tick_params(axis='both', colors='#dcdde1')

        for spin in self.__ax.spines.values():
            spin.set_color('#dcdde1')

        self.__zoom_rect = None

        self.__canvas = FigureCanvasQTAgg(self.__fig)
        self.__canvas.mpl_connect('button_press_event', self.__on_mouse_press_event)
        self.__canvas.mpl_connect('key_press_event', self.__on_key_press_event)

        self.__canvas.setFocusPolicy(Qt.ClickFocus)
        self.__canvas.setFocus()

        self.__layout = QtW.QGridLayout(self)

        self.__layout.addWidget(self.__canvas, 0, 0, 1, 2)

        button_reset_to_ww = QtW.QPushButton('Reset to whole world', self)
        button_reset_to_ww.clicked.connect(self.__reset_plot_to_wholeworld)
        button_reset_to_ww.setCursor(QCursor(Qt.PointingHandCursor))

        button_rerender = QtW.QPushButton('Rerender', self)
        button_rerender.clicked.connect(lambda: self.render_recorded_flight_plot())
        button_rerender.setCursor(QCursor(Qt.PointingHandCursor))

        button_toggle_cities = QtW.QPushButton('Toggle cities', self)
        button_toggle_cities.clicked.connect(self.__toggle_cities_visibility)
        button_toggle_cities.setCursor(QCursor(Qt.PointingHandCursor))

        label_info = QtW.QLabel('Right click - place zoom points, Left click - apply zoom, ESC - clear zoom rectangle')
        label_info.setProperty('color', 'color_vlight')
        label_info.setFixedHeight(50)

        self.__layout.addWidget(label_info, 1, 0, 1, 2, Qt.AlignHCenter)
        self.__layout.addWidget(button_reset_to_ww, 2, 0)
        self.__layout.addWidget(button_rerender, 2, 1)
        self.__layout.addWidget(button_toggle_cities, 3, 0, 1, 2)

        self.setLayout(self.__layout)
        self.setWindowTitle('Recorded flight')
        self.setStyleSheet(Settings().style)
        self.setWindowModality(Qt.WindowModality(2))

    def __calculate_constraint(self):
        x_average = (min(self.__flight_points[0]) + max(self.__flight_points[0])) / 2
        y_average = (min(self.__flight_points[1]) + max(self.__flight_points[1])) / 2
        x_lenth = max(self.__flight_points[0]) - min(self.__flight_points[0])
        y_lenth = max(self.__flight_points[1]) - min(self.__flight_points[1])
        total_length = max(x_lenth, y_lenth)

        constraint = [x_average - total_length / 2,
                      x_average + total_length / 2,
                      y_average - total_length / 2,
                      y_average + total_length / 2]

        return constraint

    def render_recorded_flight_plot(self, clear_plot=True):
        if clear_plot:
            self.__clear_plot()

        sf = Reader(Settings().path_countries)
        shapes = sf.shapes()
        suitable_shapes = {}

        for i, shape in enumerate(shapes):
            for point in shape.points:
                if PlotUtils.coordinates_suites_constraint(point, self.__constraint):
                    suitable_shapes[i] = shape
                    break

        for shape_index, shape in suitable_shapes.items():
            parts = []

            for i in range(1, len(shape.parts)):
                parts.append(shape.points[shape.parts[i-1]:(shape.parts[i] - 1)])
                parts[i-1].append(parts[i-1][0])

            parts.append(shape.points[shape.parts[-1]:len(shape.points)])
            parts[-1].append(parts[-1][0])

            for part in parts:
                xs, ys = zip(*part)
                self.__ax.plot(xs, ys, color='0.5')

        for i in range(1, len(self.__flight_points[0])):  # len(points[0]) == len(points[1]) always!
            xs = [self.__flight_points[0][i-1], self.__flight_points[0][i]]
            ys = [self.__flight_points[1][i-1], self.__flight_points[1][i]]

            self.__ax.plot(xs, ys, color=PlotUtils.choose_color_by_altitude(self.__flight_points[2][i]))

        self.__ax.axis(self.__constraint)
        self.__canvas.draw()

        self.render_cities(self.__constraint)

    def render_cities(self, constraint):
        self.__remove_cities()

        sf = Reader(Settings().path_cities)
        shapes = sf.shapes()
        records = sf.records()

        world_square = 62504  # calculated using bbox of world's sf
        current_plot_square = abs(max(constraint[0], constraint[1]) - min(constraint[0], constraint[1])) * abs(max(constraint[2], constraint[3]) - min(constraint[2], constraint[3]))
        zoom_level = int(world_square // current_plot_square)

        for city_index, city in enumerate(records):
            if PlotUtils.should_render_city(city['POP'], zoom_level):
                shape = shapes[city_index]

                if PlotUtils.coordinates_suites_constraint(shape.points[0], constraint):
                    name = city['CITY_NAME']

                    text = plt.Text(shape.points[0][0], shape.points[0][1], text=name, color='1',
                                    verticalalignment='center', horizontalalignment='center')
                    self.__ax.add_artist(text)

                    self.__rendered_cities.append(text)

        self.__canvas.draw()

    def __remove_cities(self):
        if not self.__rendered_cities:
            return

        for city in self.__rendered_cities:
            city.remove()

        self.__rendered_cities = []
        self.__canvas.draw()

    def __toggle_cities_visibility(self):
        for city in self.__rendered_cities:
            city.set_visible(False if city.get_visible() else True)
        self.__canvas.draw()

    def __clear_zoom_rect(self):
        if self.__zoom_rect:
            self.__zoom_rect.remove()
            self.__zoom_start_point = None

        self.__zoom_rect = plt.Rectangle((0, 0), 0, 0, color='#f25555')
        self.__ax.add_artist(self.__zoom_rect)

    def __clear_plot(self):
        self.__ax.clear()
        self.__constraint = self.__calculate_constraint()

        self.__clear_zoom_rect()

    def __reset_plot_to_wholeworld(self):
        self.__constraint = [-180, 180, -90, 90]
        self.render_recorded_flight_plot(False)

    def __draw_zoom_line(self, x, y):
        try:
            width = abs(x - self.__zoom_start_point[0])
            height = abs(x - self.__zoom_start_point[0])
        except TypeError:
            return

        dx = (x > self.__zoom_start_point[0])
        dy = (y > self.__zoom_start_point[1])

        if not dx:
            width = -width

        if not dy:
            height = -height

        self.__zoom_rect.update({'xy': self.__zoom_start_point, 'width': width, 'height': height})

        self.__canvas.draw()

    def __on_mouse_press_event(self, event):
        if event.button == MouseButton.RIGHT:
            if not self.__zoom_start_point:
                self.__zoom_start_point = (event.xdata, event.ydata)
            else:
                self.__draw_zoom_line(event.xdata, event.ydata)
        elif event.button == MouseButton.LEFT:
            if self.__zoom_rect.get_width() == 0 and self.__zoom_rect.get_height() == 0:
                return

            bbox_points = self.__zoom_rect.get_bbox().get_points()

            xmin = min(bbox_points[0][0], bbox_points[1][0])
            xmax = max(bbox_points[0][0], bbox_points[1][0])
            ymin = min(bbox_points[0][1], bbox_points[1][1])
            ymax = max(bbox_points[0][1], bbox_points[1][1])

            self.__constraint = [xmin, xmax, ymin, ymax]

            self.__zoom_start_point = None
            self.__zoom_rect.update({'xy': [0, 0], 'width': 0, 'height': 0})

            self.__ax.axis(self.__constraint)
            self.render_cities(self.__constraint)

    def __on_key_press_event(self, event):
        if event.key == 'escape':
            self.__clear_zoom_rect()
            self.__canvas.draw()
