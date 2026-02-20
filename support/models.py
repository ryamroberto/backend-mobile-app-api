import uuid
from django.db import models
from django.conf import settings
from common.models import TimeStampedModel

class ResolveCase(TimeStampedModel):
    class Category(models.TextChoices):
        TECHNICAL = 'TECHNICAL', 'Técnico'
        BILLING = 'BILLING', 'Faturamento'
        AI_REFINEMENT = 'AI_REFINEMENT', 'Refinamento de IA'
        OTHER = 'OTHER', 'Outro'

    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Aberto'
        IN_PROGRESS = 'IN_PROGRESS', 'Em Andamento'
        RESOLVED = 'RESOLVED', 'Resolvido'
        CLOSED = 'CLOSED', 'Fechado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='support_cases',
        verbose_name='solicitante'
    )
    title = models.CharField('título', max_length=255)
    description = models.TextField('descrição')
    
    category = models.CharField(
        'categoria',
        max_length=20,
        choices=Category.choices,
        default=Category.TECHNICAL
    )
    
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
    )
    
    resolution_notes = models.TextField('notas de resolução', blank=True, null=True)

    class Meta:
        verbose_name = 'caso de suporte'
        verbose_name_plural = 'casos de suporte'
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.title} ({self.get_status_display()})"
