import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from common.models import TimeStampedModel

class AutomationTask(TimeStampedModel):
    class TaskType(models.TextChoices):
        BEDROCK = 'BEDROCK', 'Amazon Bedrock'
        STEP_FUNCTION = 'STEP_FUNCTION', 'AWS Step Function'
        ECS = 'ECS', 'Amazon ECS'
        EKS = 'EKS', 'Elastic Kubernetes Service'
        CUSTOM = 'CUSTOM', 'Custom Automation'

    class ExecutionStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pendente'
        RUNNING = 'RUNNING', 'Em Execução'
        COMPLETED = 'COMPLETED', 'Concluída'
        FAILED = 'FAILED', 'Falhou'
        CANCELLED = 'CANCELLED', 'Cancelada'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='automation_tasks',
        verbose_name='proprietário'
    )
    title = models.CharField('título', max_length=255)
    description = models.TextField('descrição', blank=True)
    
    task_type = models.CharField(
        'tipo de tarefa',
        max_length=20,
        choices=TaskType.choices,
        default=TaskType.CUSTOM
    )
    
    provider_id = models.CharField(
        'ID do provedor (ARN/ID)',
        max_length=255,
        blank=True,
        help_text='ARN da Step Function, ID do ECS Cluster ou Modelo do Bedrock.'
    )
    
    execution_status = models.CharField(
        'status de execução',
        max_length=20,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.PENDING
    )
    
    associated_case = models.ForeignKey(
        'support.ResolveCase',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='automation_tasks',
        verbose_name='caso associado'
    )
    
    input_params = models.JSONField('parâmetros de entrada', default=dict, blank=True)
    output_results = models.JSONField('resultados da saída', default=dict, blank=True)

    class Meta:
        verbose_name = 'tarefa de automação'
        verbose_name_plural = 'tarefas de automação'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_task_type_display()} - {self.title}"

    def clean(self):
        super().clean()
        if self.task_type != self.TaskType.CUSTOM and not self.provider_id:
            raise ValidationError({
                'provider_id': 'O ID do provedor é obrigatório para tarefas que não sejam CUSTOM.'
            })
