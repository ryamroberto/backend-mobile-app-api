"""
Serializers para a API de notificações.
"""
from rest_framework import serializers
from notifications.models import DeviceToken, NotificationLog


class DeviceTokenSerializer(serializers.ModelSerializer):
    """Serializer para DeviceToken."""
    
    platform_display = serializers.CharField(
        source='get_platform_display',
        read_only=True
    )
    
    class Meta:
        model = DeviceToken
        fields = [
            'id',
            'token',
            'platform',
            'platform_display',
            'device_id',
            'device_name',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'token': {'write_only': True},
        }


class DeviceTokenRegisterSerializer(serializers.Serializer):
    """Serializer para registro de dispositivo."""
    
    token = serializers.CharField(
        max_length=500,
        required=True,
        help_text='Token do dispositivo para notificações push'
    )
    platform = serializers.ChoiceField(
        choices=DeviceToken.Platform.choices,
        required=True,
        help_text='Plataforma do dispositivo'
    )
    device_id = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text='ID único do dispositivo (opcional)'
    )
    device_name = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text='Nome do dispositivo (opcional)'
    )


class DeviceTokenUnregisterSerializer(serializers.Serializer):
    """Serializer para unregister de dispositivo."""
    
    token = serializers.CharField(
        max_length=500,
        required=True,
        help_text='Token do dispositivo a ser removido'
    )


class NotificationLogSerializer(serializers.ModelSerializer):
    """Serializer para NotificationLog."""
    
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    user_email = serializers.EmailField(
        source='user.email',
        read_only=True
    )
    
    class Meta:
        model = NotificationLog
        fields = [
            'id',
            'user',
            'user_email',
            'title',
            'body',
            'data',
            'template',
            'status',
            'status_display',
            'sent_at',
            'delivered_at',
            'error_message',
            'retry_count',
            'created_at',
        ]
        read_only_fields = fields


class SendNotificationSerializer(serializers.Serializer):
    """Serializer para envio de notificação."""
    
    user_id = serializers.IntegerField(
        required=False,
        help_text='ID do usuário destinatário (opcional para broadcast)'
    )
    title = serializers.CharField(
        max_length=255,
        required=True,
        help_text='Título da notificação'
    )
    body = serializers.CharField(
        required=True,
        help_text='Corpo da notificação'
    )
    data = serializers.DictField(
        required=False,
        help_text='Dados adicionais da notificação'
    )
    template = serializers.CharField(
        max_length=100,
        required=False,
        help_text='Template a ser utilizado'
    )
    broadcast = serializers.BooleanField(
        default=False,
        help_text='Se True, envia para todos os dispositivos'
    )
