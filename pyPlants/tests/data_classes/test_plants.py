
from django.test import TestCase, tag

from pyPlants.models import PlantUser, Plant
from pyPlants.data_classes.action_plant import ActionPlant


@tag('action-plant')
class ActionPlantTest(TestCase):
    def setUp(self):
        self.user = PlantUser.objects.create_user(
            email='foo@bar.com'
        )
        self.plant_1 = Plant.objects.create(
            name='Plant 1',
            user=self.user,
            water_frequency_summer=7,
            water_frequency_winter=14,
        )
        self.plant_2 = Plant.objects.create(
            name='Plant 2',
            user=self.user,
            water_frequency_summer=7,
            water_frequency_winter=14,
        )
        self.plant_3 = Plant.objects.create(
            name='Plant 3',
            user=self.user,
            water_frequency_summer=7,
            water_frequency_winter=14,
        )

    def test_class_init(self):
        action_plant = ActionPlant()
        # empty lists
        self.assertListEqual(action_plant.get_all_plants(), [])
        self.assertListEqual(action_plant.water, [])
        self.assertListEqual(action_plant.fertilize, [])
        self.assertListEqual(action_plant.repot, [])
        self.assertTrue(action_plant.is_empty())
        # plant names
        self.assertListEqual(action_plant.all_plant_names(), [])
        self.assertListEqual(action_plant.water_plant_names(), [])
        self.assertListEqual(action_plant.fertilize_plant_names(), [])
        self.assertListEqual(action_plant.repot_plant_names(), [])
        # plant count
        self.assertEqual(action_plant.count_all_plants(), 0)
        self.assertEqual(action_plant.count_plants_to_water(), 0)
        self.assertEqual(action_plant.count_plants_to_fertilize(), 0)
        self.assertEqual(action_plant.count_plants_to_repot(), 0)

    def test_base_adding_plants(self):
        action_plant = ActionPlant()
        # water
        action_plant.add_water(self.plant_1)
        self.assertListEqual(action_plant.water, [self.plant_1])
        self.assertListEqual(action_plant.water_plant_names(), [self.plant_1.name])
        self.assertEqual(action_plant.count_plants_to_water(), 1)
        self.assertFalse(action_plant.is_empty())
        # repot
        action_plant.add_repot(self.plant_2)
        self.assertListEqual(action_plant.repot, [self.plant_2])
        self.assertListEqual(action_plant.repot_plant_names(), [self.plant_2.name])
        self.assertEqual(action_plant.count_plants_to_repot(), 1)
        self.assertFalse(action_plant.is_empty())
        # fertilize
        action_plant.add_fertilize(self.plant_3)
        self.assertListEqual(action_plant.fertilize, [self.plant_3])
        self.assertListEqual(action_plant.fertilize_plant_names(), [self.plant_3.name])
        self.assertEqual(action_plant.count_plants_to_fertilize(), 1)
        self.assertFalse(action_plant.is_empty())
        # all
        self.assertListEqual(action_plant.get_all_plants(), [self.plant_1, self.plant_2, self.plant_3])
        self.assertListEqual(action_plant.all_plant_names(), [self.plant_1.name, self.plant_2.name, self.plant_3.name])
        self.assertEqual(action_plant.count_all_plants(), 3)

    def test_multi_plants(self):
        action_plant = ActionPlant()
        action_plant.add_water(self.plant_1)
        action_plant.add_repot(self.plant_2)
        action_plant.add_fertilize(self.plant_3)
        # add extra plants to water
        action_plant.add_water(self.plant_2)
        action_plant.add_water(self.plant_3)

        self.assertFalse(action_plant.is_empty())
        # all plants
        self.assertListEqual(action_plant.get_all_plants(), [self.plant_1, self.plant_2, self.plant_3])
        self.assertListEqual(action_plant.all_plant_names(), [self.plant_1.name, self.plant_2.name, self.plant_3.name])
        self.assertEqual(action_plant.count_all_plants(), 3)
        # water
        self.assertListEqual(action_plant.water, [self.plant_1, self.plant_2, self.plant_3])
        self.assertListEqual(action_plant.water_plant_names(), [self.plant_1.name, self.plant_2.name, self.plant_3.name])
        self.assertEqual(action_plant.count_plants_to_water(), 3)
        # repot
        self.assertListEqual(action_plant.repot, [self.plant_2])
        self.assertListEqual(action_plant.repot_plant_names(), [self.plant_2.name])
        self.assertEqual(action_plant.count_plants_to_repot(), 1)
        # fertilize
        self.assertListEqual(action_plant.fertilize, [self.plant_3])
        self.assertListEqual(action_plant.fertilize_plant_names(), [self.plant_3.name])
        self.assertEqual(action_plant.count_plants_to_fertilize(), 1)
