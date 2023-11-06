from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views.notification import NotificationModelViewSet
from api.views.notification_center import NotificationCenterModelViewSet
from api.views.plant import PlantModelViewSet
from api.views.user import UserModelViewSet

router = DefaultRouter()
router.register(r'plants', PlantModelViewSet, basename='plant')
router.register(r'notifications', NotificationModelViewSet, basename='notification')
router.register(r'notification-centers', NotificationCenterModelViewSet, basename='notification_center')
router.register(r'users', UserModelViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
