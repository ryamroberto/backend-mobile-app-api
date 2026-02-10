import uuid
from django.db import models
from django.conf import settings
from common.models import TimeStampedModel

class Resource(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Ativo'
        ARCHIVED = 'ARCHIVED', 'Arquivado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resources',
        verbose_name='proprietário'
    )
    title = models.CharField('título', max_length=255)
    description = models.TextField('descrição', blank=True)
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    metadata = models.JSONField('metadados', default=dict, blank=True)

    class Meta:
        verbose_name = 'recurso'
        verbose_name_plural = 'recursos'
        ordering = ['-created_at']

    def __str__(self):
        return self.title