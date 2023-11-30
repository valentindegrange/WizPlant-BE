from celery import shared_task

from ai.models import AIPlantAnswer
from ai.service import PlantAIService
from pyPlants.models import Plant


@shared_task(name='get_ai_plant_answer_task')
def get_ai_plant_answer_task(plant_id, ai_plant_answer_id):
    plant = Plant.objects.get(id=plant_id)
    ai_plant_answer = AIPlantAnswer.objects.get(id=ai_plant_answer_id)
    service = PlantAIService(plant=plant, ai_plant_answer=ai_plant_answer)
    res = service.get_ai_plant_answer()
    return res
