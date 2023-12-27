from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views.login import CustomAuthToken
from api.views.notification import NotificationModelViewSet
from api.views.notification_center import NotificationCenterViews
from api.views.plant import PlantModelViewSet
from api.views.signup import SignUpView
from api.views.user import UserView, ChangePasswordView
from api.views.ai_plant_answer import AIPlantAnswerViewSet

router = DefaultRouter()
router.register(r'plants', PlantModelViewSet, basename='plant')
router.register(r'notifications', NotificationModelViewSet, basename='notification')
router.register(r'ai-plant-answers', AIPlantAnswerViewSet, basename='ai-plant-answer')


urlpatterns = [
    path('', include(router.urls)),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/', UserView.as_view(), name='user'),
    path('user/change-password/', ChangePasswordView.as_view(), name='user-change-password'),
    path('notification-center/', NotificationCenterViews.as_view(), name='notification-center'),
]
