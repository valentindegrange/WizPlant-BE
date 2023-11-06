from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from api.serializers.user import UserSerializer
from pyPlants.models import PlantUser


class UserModelViewSet(viewsets.ModelViewSet):
    queryset = PlantUser.objects.all()
    serializer_class = UserSerializer
