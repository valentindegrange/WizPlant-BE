from rest_framework import serializers
from ai.models import AIPlantAnswer


class AIPlantAnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = AIPlantAnswer
        fields = '__all__'
