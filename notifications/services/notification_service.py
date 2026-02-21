"""
Notification Service para gerenciamento de notificações push.
"""
import logging
from typing import Dict, Any, Optional, List
from django.utils import timezone

from notifications.models import DeviceToken, NotificationLog
from notifications.services.fcm_service import fcm_service

logger = logging.getLogger('notifications')


class NotificationService:
    """
    Serviço de alto nível para gerenciamento de notificações.
    """
    
    # Templates de notificação embutidos
    TEMPLATES = {
        'novo_caso_suporte': {
            'title': 'Novo Caso de Suporte Criado',
            'body': 'Um novo caso de suporte foi criado: {titulo}',
            'data_template': {
                'type': 'support_case',
                'action': 'created',
                'case_id': '{case_id}',
            }
        },
        'caso_atualizado': {
            'title': 'Caso de Suporte Atualizado',
            'body': 'Seu caso de suporte foi atualizado para: {status}',
            'data_template': {
                'type': 'support_case',
                'action': 'updated',
                'case_id': '{case_id}',
            }
        },
        'tarefa_concluida': {
            'title': 'Automação Concluída',
            'body': 'A tarefa de automação foi concluída com sucesso',
            'data_template': {
                'type': 'automation',
                'action': 'completed',
                'task_id': '{task_id}',
            }
        },
        'mensagem_sistema': {
            'title': 'Mensagem do Sistema',
            'body': '{mensagem}',
            'data_template': {
                'type': 'system',
                'action': 'message',
            }
        },
    }
    
    def register_device(
        self,
        user,
        token: str,
        platform: str,
        device_id: Optional[str] = None,
        device_name: Optional[str] = None
    ) -> DeviceToken:
        """
        Registra um novo dispositivo ou atualiza existente.
        
        Args:
            user: Usuário proprietário do dispositivo.
            token: Token do dispositivo.
            platform: Plataforma (ios, android, web).
            device_id: ID do dispositivo (opcional).
            device_name: Nome do dispositivo (opcional).
        
        Returns:
            DeviceToken: Token registrado/atualizado.
        """
        # Verificar se token já existe
        existing = DeviceToken.objects.filter(token=token).first()
        
        if existing:
            # Atualizar existente
            existing.user = user
            existing.platform = platform
            existing.device_id = device_id
            existing.device_name = device_name
            existing.is_active = True
            existing.save()
            
            logger.info(f'Token de dispositivo atualizado: {token[:20]}...')
            return existing
        
        # Criar novo
        device_token = DeviceToken.objects.create(
            user=user,
            token=token,
            platform=platform,
            device_id=device_id,
            device_name=device_name,
            is_active=True
        )
        
        logger.info(f'Novo token de dispositivo registrado: {token[:20]}...')
        return device_token
    
    def unregister_device(self, token: str) -> bool:
        """
        Remove/desativa um dispositivo.
        
        Args:
            token: Token do dispositivo.
        
        Returns:
            bool: True se removido, False se não encontrado.
        """
        device_token = DeviceToken.objects.filter(token=token).first()
        
        if not device_token:
            logger.warning(f'Token não encontrado: {token[:20]}...')
            return False
        
        # Desativar token (soft delete)
        device_token.is_active = False
        device_token.save()
        
        logger.info(f'Token de dispositivo desativado: {token[:20]}...')
        return True
    
    def send_notification(
        self,
        user,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        template: Optional[str] = None,
        send_to_all_devices: bool = True
    ) -> List[NotificationLog]:
        """
        Envia notificação para um usuário.
        
        Args:
            user: Usuário destinatário.
            title: Título da notificação.
            body: Corpo da notificação.
            data: Dados adicionais (opcional).
            template: Nome do template utilizado (opcional).
            send_to_all_devices: Se True, envia para todos os dispositivos do usuário.
        
        Returns:
            list: Lista de NotificationLog criados.
        """
        # Obter tokens ativos do usuário
        tokens = DeviceToken.objects.filter(
            user=user,
            is_active=True
        )
        
        if not tokens.exists():
            logger.warning(f'Usuário {user.email} não possui dispositivos registrados')
            return []
        
        logs = []
        
        for device_token in tokens:
            # Enviar notificação
            result = fcm_service.send_to_device(
                token=device_token.token,
                title=title,
                body=body,
                data=data or {}
            )
            
            # Criar log
            log = self._create_notification_log(
                user=user,
                title=title,
                body=body,
                data=data or {},
                template=template,
                device_token=device_token,
                result=result
            )
            
            logs.append(log)
        
        return logs
    
    def send_notification_to_devices(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envia notificação para uma lista de tokens.
        
        Args:
            tokens: Lista de tokens.
            title: Título da notificação.
            body: Corpo da notificação.
            data: Dados adicionais (opcional).
            template: Nome do template utilizado (opcional).
        
        Returns:
            dict: Resultado do envio.
        """
        # Enviar via FCM
        result = fcm_service.send_to_devices(
            tokens=tokens,
            title=title,
            body=body,
            data=data or {}
        )
        
        # Criar log consolidado
        log = NotificationLog.objects.create(
            title=title,
            body=body,
            data=data or {},
            template=template,
            status=NotificationLog.Status.SENT if result.get('success_count', 0) > 0 else NotificationLog.Status.FAILED,
            sent_at=timezone.now(),
            error_message=', '.join([e.get('error', '') for e in result.get('errors', [])])
        )
        
        return {
            'result': result,
            'log': log
        }
    
    def send_broadcast(
        self,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envia notificação broadcast para todos os dispositivos.
        
        Args:
            title: Título da notificação.
            body: Corpo da notificação.
            data: Dados adicionais (opcional).
            template: Nome do template utilizado (opcional).
        
        Returns:
            dict: Resultado do envio.
        """
        # Obter todos os tokens ativos
        tokens = list(DeviceToken.objects.filter(is_active=True).values_list('token', flat=True))
        
        if not tokens:
            logger.warning('Nenhum dispositivo ativo para broadcast')
            return {
                'success': False,
                'error': 'Nenhum dispositivo ativo'
            }
        
        return self.send_notification_to_devices(
            tokens=tokens,
            title=title,
            body=body,
            data=data,
            template=template
        )
    
    def send_with_template(
        self,
        user,
        template_name: str,
        context: Dict[str, Any],
        data: Optional[Dict[str, str]] = None
    ) -> List[NotificationLog]:
        """
        Envia notificação usando um template.
        
        Args:
            user: Usuário destinatário.
            template_name: Nome do template.
            context: Contexto para preencher o template.
            data: Dados adicionais (opcional).
        
        Returns:
            list: Lista de NotificationLog criados.
        """
        if template_name not in self.TEMPLATES:
            logger.error(f'Template não encontrado: {template_name}')
            return []
        
        template = self.TEMPLATES[template_name]
        
        # Preencher título e corpo
        title = template['title'].format(**context)
        body = template['body'].format(**context)
        
        # Preencher dados do template
        template_data = {}
        for key, value in template.get('data_template', {}).items():
            template_data[key] = value.format(**context) if isinstance(value, str) else value
        
        # Mesclar com dados adicionais
        if data:
            template_data.update(data)
        
        return self.send_notification(
            user=user,
            title=title,
            body=body,
            data=template_data,
            template=template_name
        )
    
    def _create_notification_log(
        self,
        user,
        title: str,
        body: str,
        data: Dict[str, str],
        template: Optional[str],
        device_token: DeviceToken,
        result: Dict[str, Any]
    ) -> NotificationLog:
        """
        Cria um log de notificação.
        
        Args:
            user: Usuário destinatário.
            title: Título da notificação.
            body: Corpo da notificação.
            data: Dados da notificação.
            template: Template utilizado.
            device_token: Token do dispositivo.
            result: Resultado do envio FCM.
        
        Returns:
            NotificationLog: Log criado.
        """
        # Determinar status
        if result.get('success'):
            status = NotificationLog.Status.SENT
            error_message = ''
        else:
            status = NotificationLog.Status.FAILED
            error_message = result.get('error', 'Erro desconhecido')
        
        # Criar log
        log = NotificationLog.objects.create(
            user=user,
            title=title,
            body=body,
            data=data,
            template=template,
            status=status,
            sent_at=timezone.now() if result.get('success') else None,
            error_message=error_message,
            device_token=device_token,
            fcm_message_id=result.get('message_id', '')
        )
        
        return log
    
    def retry_failed_notifications(self, max_retries: int = 3) -> int:
        """
        Tenta reenviar notificações falhadas.
        
        Args:
            max_retries: Número máximo de tentativas.
        
        Returns:
            int: Número de notificações reenviadas com sucesso.
        """
        # Obter notificações falhadas com retry_count < max_retries
        failed = NotificationLog.objects.filter(
            status=NotificationLog.Status.FAILED,
            retry_count__lt=max_retries
        ).select_related('user', 'device_token')
        
        success_count = 0
        
        for log in failed:
            if not log.device_token or not log.user:
                continue
            
            # Tentar reenviar
            result = fcm_service.send_to_device(
                token=log.device_token.token,
                title=log.title,
                body=log.body,
                data=log.data
            )
            
            # Atualizar log
            log.retry_count += 1
            
            if result.get('success'):
                log.status = NotificationLog.Status.SENT
                log.sent_at = timezone.now()
                log.error_message = ''
                log.fcm_message_id = result.get('message_id', '')
                success_count += 1
            else:
                log.error_message = result.get('error', 'Erro no retry')
            
            log.save()
        
        logger.info(f'Retry concluído: {success_count}/{failed.count()} notificações recuperadas')
        return success_count


# Instância singleton do serviço
notification_service = NotificationService()
