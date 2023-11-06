class ActionPlant:
    """
    This class is used to store plants that need to be watered, repotted or fertilized.
    It also provides some useful methods to gets plant names and counts.
    """
    def __init__(self):
        self.water = list()  # plants to water
        self.repot = list()  # plants to repot
        self.fertilize = list()  # plants to fertilize

    def get_all_plants(self):
        # unique plants
        return list(set(self.water + self.repot + self.fertilize))

    def add_water(self, plant):
        self.water.append(plant)

    def add_repot(self, plant):
        self.repot.append(plant)

    def add_fertilize(self, plant):
        self.fertilize.append(plant)

    def is_empty(self):
        return not (self.water or self.repot or self.fertilize)

    def all_plant_names(self):
        return [plant.name for plant in self.get_all_plants()]

    def water_plant_names(self):
        return [plant.name for plant in self.water]

    def repot_plant_names(self):
        return [plant.name for plant in self.repot]

    def fertilize_plant_names(self):
        return [plant.name for plant in self.fertilize]

    def count_all_plants(self):
        # unique plants
        return len(self.get_all_plants())

    def count_plants_to_water(self):
        return len(self.water)

    def count_plants_to_repot(self):
        return len(self.repot)

    def count_plants_to_fertilize(self):
        return len(self.fertilize)
