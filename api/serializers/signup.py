from rest_framework import serializers
from pyPlants.models import PlantUser


class SignUpSerializer(serializers.ModelSerializer):

    class Meta:
        """Meta class."""
        model = PlantUser
        fields = ('email', 'password')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8,
                'style': {'input_type': 'password'}
            }
        }

    def create(self, validated_data):
        """Create a new user with encrypted password and return it."""
        return PlantUser.objects.create_user(**validated_data)