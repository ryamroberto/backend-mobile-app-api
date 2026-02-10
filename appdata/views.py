from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from common.permissions import IsOwner
from .models import Resource
from .serializers import ResourceSerializer

class ResourceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para visualizar e editar recursos.
    """
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        """
        Este viewset deve retornar uma lista de todos os recursos
        para o usuário autenticado no momento.
        """
        if getattr(self, 'swagger_fake_view', False):
            return Resource.objects.none()
            
        user = self.request.user
        return Resource.objects.filter(owner=user)

    def perform_create(self, serializer):
        """
        Associa o usuário autenticado como proprietário ao criar um novo recurso.
        """
        serializer.save(owner=self.request.user)