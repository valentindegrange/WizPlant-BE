from rest_framework import serializers
from pyPlants.models import Plant


class PlantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Plant
        fields = '__all__'
        # exclude user
