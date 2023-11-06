from rest_framework import serializers
from pyPlants.models import PlantUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantUser
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
        }
