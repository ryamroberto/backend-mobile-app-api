"""
URLs para o app de notificações.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from notifications.views import DeviceTokenViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r'devices', DeviceTokenViewSet, basename='device-token')
router.register(r'', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]
