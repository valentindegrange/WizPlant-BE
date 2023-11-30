from rest_framework import serializers
from pyPlants.models import Plant


class PlantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Plant
        fields = '__all__'
        read_only_fields = ('user', 'is_complete')

    def create(self, validated_data):
        user = self.context['request'].user
        plant = Plant.objects.create(**validated_data, user=user)
        return plant
