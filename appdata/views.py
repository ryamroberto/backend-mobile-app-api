from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from common.permissions import IsOwner
from .models import AutomationTask
from .serializers import AutomationTaskSerializer
from .selectors import resource_selectors
from .services import resource_services

class AutomationTaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar tarefas de automação (AI Orchestration).
    """
    serializer_class = AutomationTaskSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        """
        Retorna as tarefas do usuário autenticado.
        """
        if getattr(self, 'swagger_fake_view', False):
            return AutomationTask.objects.none()
            
        return resource_selectors.task_list_for_user(user=self.request.user)

    def perform_create(self, serializer):
        """
        Cria uma nova tarefa usando o service.
        """
        resource_services.task_create(
            user=self.request.user,
            **serializer.validated_data
        )

    def perform_update(self, serializer):
        """
        Atualiza a tarefa usando o service.
        """
        resource_services.task_update(
            task=self.get_object(),
            **serializer.validated_data
        )

    def perform_destroy(self, instance):
        """
        Deleta a tarefa usando o service.
        """
        resource_services.task_delete(task=instance)
