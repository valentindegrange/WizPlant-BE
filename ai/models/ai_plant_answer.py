from django.db import models
from pyPlants.models import Plant, AbstractPlantModel
from pyPlants.utils import plant_logos_directory_path


class AIPlantAnswer(AbstractPlantModel):
    class StatusChoice(models.TextChoices):
        SUCCESS = 'success'
        FAILURE = 'failure'
        IN_PROGRESS = 'in_progress'
        NOT_STARTED = 'not_started'

    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='ai_plant_answers')
    status = models.CharField(max_length=20, choices=StatusChoice.choices, default=StatusChoice.NOT_STARTED)
    json_answer = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to=plant_logos_directory_path)
    is_checking_image = models.BooleanField(default=False)
    is_generating_image = models.BooleanField(default=False)

    def user(self):
        return self.plant.user.email
