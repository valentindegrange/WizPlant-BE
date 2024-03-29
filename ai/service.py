import logging

from ai.client import OpenAIClient
from pyPlants.constants import Seasons
from pyPlants.models import Plant
from ai.models import AIPlantAnswer
from ai.dataclass import PlantCheckerAnswer
import requests
from django.core.files.base import ContentFile
from celery import shared_task


logger = logging.getLogger(__name__)


class PlantAIService:
    """
    Class that manages OpenAI plant recognition and instructions generation.
    """
    def __init__(self, plant: Plant, ai_plant_answer: AIPlantAnswer = None):
        logger.info(f'Initializing AI service for plant {plant.id}')
        self.plant = plant
        user = self.plant.user
        if not user.has_ai_enabled:
            raise PermissionError('User does not have AI enabled')
        if user.has_reached_max_ai_usage():
            raise PermissionError('User has reached max AI usage (50)')
        self.client = OpenAIClient(default_language=user.get_default_language_display())

        if not ai_plant_answer:
            self.ai_plant_answer = AIPlantAnswer.objects.create(plant=self.plant)
        else:
            self.ai_plant_answer = ai_plant_answer

        self.has_plant_name = self.plant.name is not None and self.plant.name != ''
        self.has_plant_image = True if self.plant.image.name else False
        if not self.has_plant_name and not self.has_plant_image:
            self.ai_plant_answer.status = AIPlantAnswer.StatusChoice.FAILURE
            self.ai_plant_answer.error_message = 'Plant does not have name or image'
            self.ai_plant_answer.save()
            raise ValueError('Plant does not have name or image')
        if not self.has_plant_name:
            self.ai_plant_answer.is_checking_image = True
            self.ai_plant_answer.save()
        if not self.has_plant_image:
            self.ai_plant_answer.is_generating_image = True
            self.ai_plant_answer.save()
        logger.info(f'AI service initialized for plant {plant.id}')

    def get_ai_plant_answer(self):
        """
        Gets the AI plant answer from the OpenAI API.
        It will first try to get the plant name from the image, if it doesn't have one.
        Then based on the plant name, it will get the plant instructions.
        Last, it will store the answer into the associated AIPlantAnswer object.
        In case of failure, it will raise an exception and store the failure message into the AIPlantAnswer object.
        """
        plant_name = self.plant.name
        # starts the process
        self.ai_plant_answer.status = AIPlantAnswer.StatusChoice.IN_PROGRESS
        self.ai_plant_answer.save()
        try:
            # try to get plant name from image
            if not self.has_plant_name:
                logger.info(f'Plant {self.plant.id} does not have name, trying to get it from image')
                response = self.client.plant_recognizer(self.plant.image.path)
                logger.info(f'Plant {self.plant.id} image recognition response: {response}')
                decoded_response = self.client.decode_response(response)
                logger.info(f'Plant {self.plant.id} image recognition decoded response: {decoded_response}')
                if 'unknown' in decoded_response:
                    logger.info(f'Plant {self.plant.id} could not be recognized from image')
                    raise ValueError('Plant could not be recognized from image')
                plant_name = decoded_response
            # get plants instructions
            logger.info(f'Getting plant instructions for {plant_name}')
            response = self.client.plant_checker(plant_name)
            logger.info(f'Plant instructions response: {response}')
            decoded_response = self.client.decode_json_response(response)
            logger.info(f'Plant instructions decoded response: {decoded_response}')
            # check if response is valid
            if 'error' in decoded_response:
                logger.info(f'Plant name {plant_name} could not be recognized')
                raise ValueError('Plant name could not be recognized')
            # check if response is properly formatted
            if not PlantCheckerAnswer.is_json_valid(decoded_response):
                raise ValueError('Plant instructions are not properly formatted')
            else:
                plant_checker_answer = PlantCheckerAnswer.from_json_answer(decoded_response, plant_name)
                self.ai_plant_answer.json_answer = plant_checker_answer.to_json()
                self.ai_plant_answer.save()
            # Generate an image of the plant if it doesn't have one
            if not self.has_plant_image:
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
        else:
            self.ai_plant_answer.status = AIPlantAnswer.StatusChoice.SUCCESS
            self.ai_plant_answer.save()
            return self.ai_plant_answer
        finally:
            return self.ai_plant_answer.status

    def update_plant_from_ai_plant_answer(self):
        """
        Updates the plant from the AIPlantAnswer object.
        """
        if self.ai_plant_answer.status != AIPlantAnswer.StatusChoice.SUCCESS:
            raise ValueError('Plant answer is not successful')
        plant_checker_answer = PlantCheckerAnswer(**self.ai_plant_answer.json_answer)
        self.plant.name = plant_checker_answer.name
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
