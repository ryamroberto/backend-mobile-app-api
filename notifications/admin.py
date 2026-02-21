"""
Admin Django para o app de notificações.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from notifications.models import DeviceToken, NotificationLog
from notifications.services.notification_service import notification_service


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    """Admin para DeviceToken."""
    
    list_display = ['user_email', 'platform', 'device_name', 'is_active', 'created_at']
    list_filter = ['platform', 'is_active', 'created_at']
    search_fields = ['user__email', 'token', 'device_id', 'device_name']
    readonly_fields = ['created_at', 'updated_at']
    
    def user_email(self, obj):
        """Retorna email do usuário com link."""
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return '-'
    
    user_email.short_description = 'Usuário'


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    """Admin para NotificationLog."""
    
    list_display = ['title', 'user_email', 'status', 'template', 'sent_at', 'retry_count']
    list_filter = ['status', 'template', 'created_at']
    search_fields = ['title', 'body', 'user__email']
    readonly_fields = [
        'user', 'title', 'body', 'data', 'template', 'status',
        'sent_at', 'delivered_at', 'error_message', 'retry_count',
        'device_token', 'fcm_message_id', 'created_at'
    ]
    date_hierarchy = 'created_at'
    
    def user_email(self, obj):
        """Retorna email do usuário com link."""
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return '-'
    
    user_email.short_description = 'Usuário'
    
    def has_add_permission(self, request):
        """Desabilita criação manual de logs."""
        return False
    
    @admin.action(description='Reenviar notificações selecionadas')
    def retry_notifications(self, request, queryset):
        """Reenvia notificações falhadas selecionadas."""
        failed = queryset.filter(status=NotificationLog.Status.FAILED)
        
        success_count = 0
        for log in failed:
            if log.device_token and log.user:
                result = notification_service.send_notification(
                    user=log.user,
                    title=log.title,
                    body=log.body,
                    data=log.data
                )
                if result:
                    success_count += 1
        
        self.message_user(request, f'{success_count} notificações reenviadas com sucesso')
    
    actions = ['retry_notifications']
