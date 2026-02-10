from django.db import models
from django.conf import settings
from common.models import TimeStampedModel

class Profile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='usuário'
    )
    full_name = models.CharField('nome completo', max_length=255, blank=True)
    bio = models.TextField('biografia', blank=True)
    avatar = models.ImageField('avatar', upload_to='avatars/', null=True, blank=True)

    class Meta:
        verbose_name = 'perfil'
        verbose_name_plural = 'perfis'

    def __str__(self):
        return f'Perfil de {self.user.email}'