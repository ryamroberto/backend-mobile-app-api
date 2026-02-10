from django.db import models

class TimeStampedModel(models.Model):
    """
    Um modelo base abstrato que fornece campos auto-atualizáveis
    'created_at' e 'updated_at'.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True