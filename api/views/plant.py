from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers.plant import PlantSerializer
from pyPlants.models import Plant


class PlantModelViewSet(viewsets.ModelViewSet):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer

    @action(methods=['post'], detail=True)
    def water(self, request, pk=None):
        plant = self.get_object()
        plant.water()
        return Response(status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def fertilize(self, request, pk=None):
        plant = self.get_object()
        plant.fertilize()
        return Response(status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def repot(self, request, pk=None):
        plant = self.get_object()
        plant.repot()
        return Response(status=status.HTTP_200_OK)
