from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResourceViewSet

# Cria um roteador e registra nosso viewset com ele.
router = DefaultRouter()
router.register(r'resources', ResourceViewSet, basename='resource')

# As URLs da API agora são determinadas automaticamente pelo roteador.
urlpatterns = [
    path('', include(router.urls)),
]
