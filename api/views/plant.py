from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as dj_filters
from django.db import models

from ai.models import AIPlantAnswer
from ai.service import PlantAIService
from ai.tasks import get_ai_plant_answer_task
from api.serializers.ai_plant_answer import AIPlantAnswerSerializer
from api.serializers.plant import PlantSerializer
from api.utils import CustomPagination
from pyPlants.models import Plant


class PlantFilter(dj_filters.FilterSet):
    class Meta:
        model = Plant
        fields = {
            'name': ['icontains'],
            'fertilizer': ['exact'],
            'repotting': ['exact'],
            'is_complete': ['exact'],
            'needs_care': ['exact']
        }
        filter_overrides = {
            models.GeneratedField:{
                'filter_class': dj_filters.BooleanFilter
            }
        }


class PlantModelViewSet(viewsets.ModelViewSet):
    serializer_class = PlantSerializer
    pagination_class = CustomPagination
    filter_backends = [dj_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PlantFilter
    search_fields = ('name', 'description')
    ordering_fields = '__all__'

    def get_queryset(self):
        return Plant.objects.filter(user=self.request.user)

    @action(methods=['post'], detail=True)
    def water(self, request, pk=None):
        plant = self.get_object()
        plant.water()
        plant.refresh_from_db()
        serializer = self.get_serializer(plant, many=False)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def fertilize(self, request, pk=None):
        plant = self.get_object()
        try:
            plant.fertilize()
            plant.refresh_from_db()
            serializer = self.get_serializer(plant, many=False)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except ValueError as err:
            return Response(data={'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True)
    def repot(self, request, pk=None):
        plant = self.get_object()
        try:
            plant.repot()
            plant.refresh_from_db()
            serializer = self.get_serializer(plant, many=False)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except ValueError as err:
            return Response(data={'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True)
    def ai_check(self, request, pk=None):
        plant = self.get_object()
        try:
            ai_plant_answer = None
            qs = plant.ai_plant_answers.filter(
                status__in=[AIPlantAnswer.StatusChoice.IN_PROGRESS, AIPlantAnswer.StatusChoice.NOT_STARTED]
            )
            if qs.exists():
                ai_plant_answer = qs.latest('created')
            ai_service = PlantAIService(plant=plant, ai_plant_answer=ai_plant_answer)
            get_ai_plant_answer_task.delay(plant_id=plant.id, ai_plant_answer_id=ai_service.ai_plant_answer.id)
            ai_plant_answer = ai_service.ai_plant_answer
            serializer = AIPlantAnswerSerializer(ai_plant_answer, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError as err:
            return Response(data={'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False)
    def next_needs_care(self, request):
        queryset = self.get_queryset()
        plant = queryset.filter(needs_care=True).first()
        data = dict(plant=None)
        if plant:
            data['plant'] = plant.id
        return Response(data, status=status.HTTP_200_OK)
