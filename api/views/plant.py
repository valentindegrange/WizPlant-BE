from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as dj_filters

from api.serializers.plant import PlantSerializer
from pyPlants.models import Plant


class PlantModelViewSet(viewsets.ModelViewSet):
    serializer_class = PlantSerializer
    filter_backends = [dj_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ('name',)
    search_fields = ('name', 'description')
    ordering_fields = '__all__'
    ordering = ['last_watered']

    def get_queryset(self):
        return Plant.objects.all()

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
