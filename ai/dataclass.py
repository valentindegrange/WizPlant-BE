from dataclasses import dataclass


@dataclass
class PlantCheckerAnswer:
    name: str
    description: str
    water_frequency_summer: int
    water_frequency_winter: int
    sunlight: str
    sun_exposure: str
    fertilizer: bool
    fertilizer_season: str
    repotting: bool
    repotting_season: str
    leaf_mist: bool
    extra_tips: str

    @staticmethod
    def plant_checker_keys():
        return ['description', 'water_frequency_summer', 'water_frequency_winter', 'sunlight', 'sun_exposure',
                'fertilizer', 'fertilizer_season', 'repotting', 'repotting_season', 'leaf_mist', 'extra_tips']

    @staticmethod
    def is_json_valid(json_answer):
        return all(key in json_answer for key in PlantCheckerAnswer.plant_checker_keys())

    @staticmethod
    def from_json_answer(json_answer, plant_name: str):
        return PlantCheckerAnswer(
            name=plant_name,
            description=json_answer['description'],
            water_frequency_summer=json_answer['water_frequency_summer'],
            water_frequency_winter=json_answer['water_frequency_winter'],
            sunlight=json_answer['sunlight'],
            sun_exposure=json_answer['sun_exposure'],
            fertilizer=json_answer['fertilizer'],
            fertilizer_season=json_answer['fertilizer_season'],
            repotting=json_answer['repotting'],
            repotting_season=json_answer['repotting_season'],
            leaf_mist=json_answer['leaf_mist'],
            extra_tips=json_answer['extra_tips']
        )

    def to_json(self):
        return {
            'name': self.name,
            'description': self.description,
            'water_frequency_summer': self.water_frequency_summer,
            'water_frequency_winter': self.water_frequency_winter,
            'sunlight': self.sunlight,
            'sun_exposure': self.sun_exposure,
            'fertilizer': self.fertilizer,
            'fertilizer_season': self.fertilizer_season,
            'repotting': self.repotting,
            'repotting_season': self.repotting_season,
            'leaf_mist': self.leaf_mist,
            'extra_tips': self.extra_tips
        }
