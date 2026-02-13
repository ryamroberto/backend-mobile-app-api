from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from common.permissions import IsOwner
from .models import Resource
from .serializers import ResourceSerializer
from .selectors import resource_selectors
from .services import resource_services

class ResourceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para visualizar e editar recursos usando Service Layer e Selectors.
    """
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        """
        Utiliza o selector para filtrar recursos do usuário.
        """
        if getattr(self, 'swagger_fake_view', False):
            return Resource.objects.none()
            
        return resource_selectors.resource_list_for_user(user=self.request.user)

    def perform_create(self, serializer):
        """
        Utiliza o service para criar um novo recurso.
        """
        resource_services.resource_create(
            user=self.request.user,
            **serializer.validated_data
        )

    def perform_update(self, serializer):
        """
        Utiliza o service para atualizar um recurso existente.
        """
        resource_services.resource_update(
            resource=self.instance if hasattr(self, 'instance') else self.get_object(),
            **serializer.validated_data
        )

    def perform_destroy(self, instance):
        """
        Utiliza o service para deletar um recurso.
        """
        resource_services.resource_delete(resource=instance)