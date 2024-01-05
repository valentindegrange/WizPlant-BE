from rest_framework import serializers
from pyPlants.models import PlantUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantUser
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'default_language', 'has_ai_enabled']
        read_only_fields = ['has_ai_enabled']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
