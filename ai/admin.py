from django.contrib import admin
from ai.models import AIPlantAnswer


class AIPlantAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'plant', 'status', 'created', 'error_message')
    list_filter = ('status', 'plant__name')
    search_fields = ('plant__name', 'error_message')


admin.site.register(AIPlantAnswer, AIPlantAnswerAdmin)
