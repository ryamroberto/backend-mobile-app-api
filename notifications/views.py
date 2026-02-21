"""
Views para a API de notificações.
"""
import logging
from rest_framework import viewsets, status, decorators, permissions
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from notifications.models import DeviceToken, NotificationLog
from notifications.serializers import (
    DeviceTokenSerializer,
    DeviceTokenRegisterSerializer,
    DeviceTokenUnregisterSerializer,
    NotificationLogSerializer,
    SendNotificationSerializer,
)
from notifications.services.notification_service import notification_service

logger = logging.getLogger('notifications')
User = get_user_model()


class DeviceTokenViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de tokens de dispositivo.
    
    Endpoints:
    - POST /api/v1/notifications/register/ - Registrar dispositivo
    - DELETE /api/v1/notifications/unregister/ - Remover dispositivo
    - GET /api/v1/notifications/devices/ - Listar dispositivos do usuário
    """
    
    serializer_class = DeviceTokenSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Retorna apenas tokens do usuário autenticado."""
        return DeviceToken.objects.filter(user=self.request.user)
    
    @decorators.action(detail=False, methods=['post'])
    def register(self, request):
        """
        Registrar um novo dispositivo para notificações push.
        
        Request:
        {
            "token": "device-token-string",
            "platform": "android|ios|web",
            "device_id": "optional-device-id",
            "device_name": "optional-device-name"
        }
        """
        serializer = DeviceTokenRegisterSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'erro': 'Dados inválidos',
                'detalhes': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            device_token = notification_service.register_device(
                user=request.user,
                token=serializer.validated_data['token'],
                platform=serializer.validated_data['platform'],
                device_id=serializer.validated_data.get('device_id'),
                device_name=serializer.validated_data.get('device_name')
            )
            
            return Response({
                'mensagem': 'Dispositivo registrado com sucesso',
                'device': DeviceTokenSerializer(device_token).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f'Erro ao registrar dispositivo: {e}')
            return Response({
                'erro': 'Erro ao registrar dispositivo',
                'detalhes': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @decorators.action(detail=False, methods=['delete'])
    def unregister(self, request):
        """
        Remover/desativar um dispositivo.
        
        Request:
        {
            "token": "device-token-string"
        }
        """
        serializer = DeviceTokenUnregisterSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'erro': 'Dados inválidos',
                'detalhes': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            success = notification_service.unregister_device(
                token=serializer.validated_data['token']
            )
            
            if success:
                return Response({
                    'mensagem': 'Dispositivo removido com sucesso'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'mensagem': 'Token não encontrado'
                }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            logger.error(f'Erro ao remover dispositivo: {e}')
            return Response({
                'erro': 'Erro ao remover dispositivo',
                'detalhes': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de notificações.
    
    Endpoints:
    - POST /api/v1/notifications/send/ - Enviar notificação (admin/staff)
    - GET /api/v1/notifications/history/ - Histórico de notificações do usuário
    - GET /api/v1/notifications/ - Listar todas (admin/staff)
    """
    
    serializer_class = NotificationLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Usuários comuns veem apenas suas notificações.
        Staff vê todas as notificações.
        """
        if self.request.user.is_staff:
            return NotificationLog.objects.all()
        return NotificationLog.objects.filter(user=self.request.user)
    
    @decorators.action(detail=False, methods=['post'])
    def send(self, request):
        """
        Enviar notificação (apenas staff/admin).
        
        Request:
        {
            "user_id": 1,  // Opcional (se broadcast=True)
            "title": "Título da notificação",
            "body": "Corpo da notificação",
            "data": {"key": "value"},  // Opcional
            "template": "nome_template",  // Opcional
            "broadcast": false  // Se True, envia para todos
        }
        """
        # Verificar permissão
        if not request.user.is_staff:
            return Response({
                'erro': 'Apenas staff pode enviar notificações'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SendNotificationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'erro': 'Dados inválidos',
                'detalhes': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Broadcast
            if serializer.validated_data.get('broadcast'):
                result = notification_service.send_broadcast(
                    title=serializer.validated_data['title'],
                    body=serializer.validated_data['body'],
                    data=serializer.validated_data.get('data'),
                    template=serializer.validated_data.get('template')
                )
                
                return Response({
                    'mensagem': 'Notificação broadcast enviada',
                    'resultado': result
                }, status=status.HTTP_200_OK)
            
            # Enviar com template
            elif serializer.validated_data.get('template'):
                user_id = serializer.validated_data.get('user_id')
                if not user_id:
                    return Response({
                        'erro': 'user_id é obrigatório quando usando template'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                user = User.objects.get(pk=user_id)
                logs = notification_service.send_with_template(
                    user=user,
                    template_name=serializer.validated_data['template'],
                    context=serializer.validated_data.get('data', {}),
                    data=serializer.validated_data.get('data')
                )
                
                return Response({
                    'mensagem': f'Notificação enviada para {len(logs)} dispositivos',
                    'logs': NotificationLogSerializer(logs, many=True).data
                }, status=status.HTTP_200_OK)
            
            # Enviar notificação simples
            else:
                user_id = serializer.validated_data.get('user_id')
                if not user_id:
                    return Response({
                        'erro': 'user_id é obrigatório para notificação individual'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                user = User.objects.get(pk=user_id)
                logs = notification_service.send_notification(
                    user=user,
                    title=serializer.validated_data['title'],
                    body=serializer.validated_data['body'],
                    data=serializer.validated_data.get('data'),
                    template=serializer.validated_data.get('template')
                )
                
                return Response({
                    'mensagem': f'Notificação enviada para {len(logs)} dispositivos',
                    'logs': NotificationLogSerializer(logs, many=True).data
                }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'erro': 'Usuário não encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.error(f'Erro ao enviar notificação: {e}')
            return Response({
                'erro': 'Erro ao enviar notificação',
                'detalhes': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @decorators.action(detail=False, methods=['get'])
    def history(self, request):
        """
        Obter histórico de notificações do usuário autenticado.
        
        Query params:
        - limit: Número de resultados (default: 50)
        - status: Filtrar por status (opcional)
        """
        limit = int(request.query_params.get('limit', 50))
        status_filter = request.query_params.get('status')
        
        queryset = NotificationLog.objects.filter(user=request.user).order_by('-created_at')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        queryset = queryset[:limit]
        
        serializer = NotificationLogSerializer(queryset, many=True)
        
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
