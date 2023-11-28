from ai.client import OpenAIClient
from pyPlants.constants import Seasons
from pyPlants.models import Plant
from ai.models import AIPlantAnswer
from ai.dataclass import PlantCheckerAnswer
import requests
from django.core.files.base import ContentFile
from celery import shared_task


class PlantAIService:
    """
    Class that manages OpenAI plant recognition and instructions generation.
    """
    def __init__(self, plant: Plant, ai_plant_answer: AIPlantAnswer = None):
        self.plant = plant
        user = self.plant.user
        if not user.has_ai_enabled:
            raise PermissionError('User does not have AI enabled')
        self.client = OpenAIClient()
        if not ai_plant_answer:
            self.ai_plant_answer = AIPlantAnswer.objects.create(plant=self.plant)

    @shared_task(name='get_ai_plant_answer')
    def get_ai_plant_answer(self):
        """
        Gets the AI plant answer from the OpenAI API.
        It will first try to get the plant name from the image, if it doesn't have one.
        Then based on the plant name, it will get the plant instructions.
        Last, it will store the answer into the associated AIPlantAnswer object.
        In case of failure, it will raise an exception and store the failure message into the AIPlantAnswer object.
        """
        has_plant_name = self.plant.name is not None
        has_plant_image = True if self.plant.image.name else False
        plant_name = self.plant.name
        if not has_plant_name and not has_plant_image:
            self.ai_plant_answer.status = AIPlantAnswer.StatusChoice.FAILURE
            self.ai_plant_answer.error_message = 'Plant does not have name or image'
            self.ai_plant_answer.save()
            raise ValueError('Plant does not have name or image')
        # starts the process
        self.ai_plant_answer.status = AIPlantAnswer.StatusChoice.IN_PROGRESS
        self.ai_plant_answer.save()
        try:
            # try to get plant name from image
            if not has_plant_name:
                response = self.client.plant_recognizer(self.plant.image.path)
                decoded_response = self.client.decode_response(response)
                if 'unknown' in decoded_response:
                    raise ValueError('Plant could not be recognized')
                plant_name = decoded_response
            # get plants instructions
            response = self.client.plant_checker(plant_name)
            decoded_response = self.client.decode_json_response(response)
            # check if response is valid
            if 'error' in decoded_response:
                raise ValueError('Plant could not be recognized')
            # check if response is properly formatted
            if not PlantCheckerAnswer.is_json_valid(decoded_response):
                raise ValueError('Plant instructions are not properly formatted')
            else:
                plant_checker_answer = PlantCheckerAnswer.from_json_answer(decoded_response, plant_name)
                self.ai_plant_answer.json_answer = plant_checker_answer.to_json()
                self.ai_plant_answer.save()
            # Generate an image of the plant if it doesn't have one
            if not has_plant_image:
                response = self.client.plant_image_generator(plant_name)
                # omitting decoding for now
                url = response.data[0].url
                image_response = requests.get(url)
                if image_response.status_code == 200:
                    image_name = f'{plant_name}.png'
                    image_file = ContentFile(image_response.content, name=image_name)
                    self.ai_plant_answer.image.save(image_name, image_file, save=True)
        except Exception as ex:
            self.ai_plant_answer.status = AIPlantAnswer.StatusChoice.FAILURE
            self.ai_plant_answer.error_message = str(ex)
            self.ai_plant_answer.save()
            raise ex
        finally:
            self.ai_plant_answer.status = AIPlantAnswer.StatusChoice.SUCCESS
            self.ai_plant_answer.save()
            return self.ai_plant_answer

    def update_plant_from_ai_plant_answer(self):
        """
        Updates the plant from the AIPlantAnswer object.
        """
        if self.ai_plant_answer.status != AIPlantAnswer.StatusChoice.SUCCESS:
            raise ValueError('Plant answer is not successful')
        plant_checker_answer = PlantCheckerAnswer(**self.ai_plant_answer.json_answer)
        self.plant.description = plant_checker_answer.description
        self.plant.water_frequency_summer = plant_checker_answer.water_frequency_summer
        self.plant.water_frequency_winter = plant_checker_answer.water_frequency_winter
        self.plant.sunlight = Plant.SunlightOptions[plant_checker_answer.sunlight.upper()]
        self.plant.sun_exposure = Plant.SunExposureOptions[plant_checker_answer.sun_exposure.upper()]
        self.plant.fertilizer = plant_checker_answer.fertilizer
        self.plant.fertilizer_season = getattr(Seasons, plant_checker_answer.fertilizer_season.upper())
        self.plant.repotting = plant_checker_answer.repotting
        self.plant.repotting_season = getattr(Seasons, plant_checker_answer.repotting_season.upper())
        self.plant.leaf_mist = plant_checker_answer.leaf_mist
        self.plant.extra_tips = plant_checker_answer.extra_tips
        self.plant.save()
        if self.ai_plant_answer.image.name:
            self.plant.image.save(self.ai_plant_answer.image.name, self.ai_plant_answer.image, save=True)
        return self.plant
