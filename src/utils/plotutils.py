class PlotUtils:
    @staticmethod
    def coordinates_suites_constraint(crds, cstr):
        if cstr[0] < crds[0] < cstr[1] and cstr[2] < crds[1] < cstr[3]:
            return True
        return False

    @staticmethod
    def coordinates_suites_constraint_text(crds, cstr):
        new_constraint = []
        for cst in cstr:
            if cst < 0:
                new_constraint.append(cst + 2)
            else:
                new_constraint.append(cst - 2)

        if new_constraint[0] < crds[0] < new_constraint[1] and new_constraint[2] < crds[1] < new_constraint[3]:
            return True
        return False

    @staticmethod
    def should_render_city(population, zoom_lvl):
        if population >= 5000000:
            return True

        if population >= 1000000:
            if zoom_lvl >= 10:
                return True
            return False

        if population >= 500000:
            if zoom_lvl >= 20:
                return True
            return False

        if population >= 350000:
            if zoom_lvl >= 35:
                return True
            return False

        if population >= 100000:
            if zoom_lvl >= 80:
                return True
            return False

        if population >= 75000:
            if zoom_lvl >= 120:
                return True
            return False

        if population >= 50000:
            if zoom_lvl >= 180:
                return True
            return False

        if population >= 35000:
            if zoom_lvl >= 200:
                return True
            return False

        if population >= 25000:
            if zoom_lvl >= 230:
                return True
            return False

        if population < 25000:
            if zoom_lvl >= 250:
                return True
            return False

    @staticmethod
    def choose_color_by_altitude(altitude):
        if altitude < 1000:
            return '#55d955'

        if 1000 <= altitude < 5000:
            return '#d0d955'

        if 5000 <= altitude < 10000:
            return '#d9a455'

        if 10000 <= altitude < 15000:
            return '#d97c55'

        if 15000 <= altitude < 20000:
            return '#d96255'

        if 20000 <= altitude < 25000:
            return '#f03e3e'

        if 25000 <= altitude < 30000:
            return '#de4591'

        if 30000 <= altitude < 35000:
            return '#de45d9'

        if altitude >= 35000:
            return '#a22ef0'
