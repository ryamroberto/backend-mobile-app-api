from django.db import models
from django.conf import settings
from common.models import TimeStampedModel


class DeviceToken(TimeStampedModel):
    """
    Modelo para armazenar tokens de dispositivos móveis para notificações push.
    """
    
    class Platform(models.TextChoices):
        """Plataformas suportadas."""
        IOS = 'ios', 'iOS (APNS)'
        ANDROID = 'android', 'Android (FCM)'
        WEB = 'web', 'Web Push'
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='device_tokens',
        help_text='Usuário proprietário do dispositivo'
    )
    token = models.CharField(
        max_length=500,
        unique=True,
        db_index=True,
        help_text='Token do dispositivo para notificações push'
    )
    platform = models.CharField(
        max_length=20,
        choices=Platform.choices,
        default=Platform.ANDROID,
        help_text='Plataforma do dispositivo'
    )
    device_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='ID único do dispositivo (opcional)'
    )
    device_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Nome do dispositivo (opcional)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Indica se o token está ativo para recebimento de notificações'
    )
    
    class Meta:
        verbose_name = 'Token de Dispositivo'
        verbose_name_plural = 'Tokens de Dispositivo'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['platform', 'is_active']),
        ]
    
    def __str__(self):
        return f'{self.get_platform_display()} - {self.device_name or "Dispositivo"} - {self.user.email}'


class NotificationLog(TimeStampedModel):
    """
    Modelo para registrar histórico de notificações enviadas.
    """
    
    class Status(models.TextChoices):
        """Status de entrega da notificação."""
        PENDING = 'pending', 'Pendente'
        SENT = 'sent', 'Enviada'
        DELIVERED = 'delivered', 'Entregue'
        FAILED = 'failed', 'Falhou'
        CANCELLED = 'cancelled', 'Cancelada'
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_logs',
        null=True,
        blank=True,
        help_text='Usuário destinatário (opcional para broadcasts)'
    )
    title = models.CharField(
        max_length=255,
        help_text='Título da notificação'
    )
    body = models.TextField(
        help_text='Corpo/mensagem da notificação'
    )
    data = models.JSONField(
        default=dict,
        blank=True,
        help_text='Dados adicionais da notificação (payload)'
    )
    template = models.CharField(
        max_length=100,
        blank=True,
        help_text='Template utilizado (se aplicável)'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text='Status de entrega da notificação'
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Data/hora de envio'
    )
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Data/hora de entrega confirmada'
    )
    error_message = models.TextField(
        blank=True,
        help_text='Mensagem de erro (se falhou)'
    )
    retry_count = models.IntegerField(
        default=0,
        help_text='Número de tentativas de reenvio'
    )
    
    # Metadados de envio
    device_token = models.ForeignKey(
        DeviceToken,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notification_logs',
        help_text='Token de dispositivo utilizado'
    )
    fcm_message_id = models.CharField(
        max_length=255,
        blank=True,
        help_text='ID da mensagem no Firebase (se disponível)'
    )
    
    class Meta:
        verbose_name = 'Log de Notificação'
        verbose_name_plural = 'Logs de Notificações'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['template', 'created_at']),
        ]
    
    def __str__(self):
        return f'{self.title} - {self.get_status_display()} - {self.created_at}'
