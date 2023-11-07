from rest_framework import serializers
from pyPlants.models import PlantUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantUser
        fields = ['email', 'first_name', 'last_name', 'phone_number']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
