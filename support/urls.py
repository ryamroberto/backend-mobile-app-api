from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResolveCaseViewSet

router = DefaultRouter()
router.register(r'cases', ResolveCaseViewSet, basename='cases')

urlpatterns = [
    path('', include(router.urls)),
]
