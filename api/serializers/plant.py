from rest_framework import serializers
from pyPlants.models import Plant


class PlantSerializer(serializers.ModelSerializer):
    should_water = serializers.SerializerMethodField()
    should_fertilize = serializers.SerializerMethodField()
    should_repot = serializers.SerializerMethodField()
    next_water_date = serializers.SerializerMethodField()
    next_fertilize_date = serializers.SerializerMethodField()
    next_repotting_date = serializers.SerializerMethodField()

    class Meta:
        model = Plant
        fields = '__all__'
        # exclude user

    def get_should_water(self, obj):
        return obj.should_water()

    def get_should_fertilize(self, obj):
        return obj.should_fertilize()

    def get_should_repot(self, obj):
        return obj.should_repot()

    def get_next_water_date(self, obj):
        return obj.next_water_date()

    def get_next_fertilize_date(self, obj):
        return obj.get_next_fertilize_date()

    def get_next_repotting_date(self, obj):
        return obj.get_next_repotting_date()
