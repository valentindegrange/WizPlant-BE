from rest_framework import serializers
from pyPlants.models import Plant


class PlantSerializer(serializers.ModelSerializer):
    water_frequency = serializers.SerializerMethodField()

    class Meta:
        model = Plant
        fields = '__all__'
        read_only_fields = ('user', 'is_complete', 'needs_care')

    def create(self, validated_data):
        user = self.context['request'].user
        plant = Plant.objects.create(**validated_data, user=user)
        return plant

    def get_water_frequency(self, obj):
        return obj.get_water_frequency()
