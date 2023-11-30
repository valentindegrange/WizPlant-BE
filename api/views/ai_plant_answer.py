from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed

from django_filters import rest_framework as dj_filters
from rest_framework.response import Response

from ai.models import AIPlantAnswer
from ai.service import PlantAIService
from api.serializers.ai_plant_answer import AIPlantAnswerSerializer


class AIPlantAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = AIPlantAnswerSerializer
    filter_backends = [dj_filters.DjangoFilterBackend]
    filterset_fields = ('status', 'plant')

    def get_queryset(self):
        queryset = AIPlantAnswer.objects.filter(plant__user=self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed("POST", detail="Creation not allowed.")

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT", detail="Updating not allowed.")

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PATCH", detail="Partial updating not allowed.")

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed("DELETE", detail="Deletion not allowed.")

    @action(methods=['post'], detail=True)
    def approve_ai_answer(self, request, pk=None):
        ai_plant_answer = self.get_object()
        if ai_plant_answer.status != AIPlantAnswer.StatusChoice.SUCCESS:
            return Response(data={'error': 'Wrong status.'}, status=status.HTTP_400_BAD_REQUEST)
        plant = ai_plant_answer.plant
        service = PlantAIService(plant=plant, ai_plant_answer=ai_plant_answer)
        service.update_plant_from_ai_plant_answer()
        return Response(status=status.HTTP_200_OK)
