class Settings:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_Settings__instance'):
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self.__path_countries = 'C:/Users/osx11/Desktop/World_Countries/World_Countries'
        self.__path_cities = 'C:/Users/osx11/Desktop/World_Cities/World_Cities'
        self.__database_file = 'C:/Users/osx11/Documents/Pycharm/Python test/src/flightstatistics.db'

        self.__style = str()
        with open('gui/styles/style.css') as f:
            for l in f:
                self.__style += l

    @property
    def path_countries(self):
        return self.__path_countries

    @property
    def path_cities(self):
        return self.__path_cities

    @property
    def style(self):
        return self.__style

    @property
    def database_file(self):
        return self.__database_file
