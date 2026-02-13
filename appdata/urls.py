from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AutomationTaskViewSet

router = DefaultRouter()
router.register(r'tasks', AutomationTaskViewSet, basename='tasks')

urlpatterns = [
    path('', include(router.urls)),
]
