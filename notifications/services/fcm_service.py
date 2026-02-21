"""
Firebase Cloud Messaging (FCM) Service para envio de notificações push.
"""
import logging
from typing import List, Dict, Any, Optional
from django.utils import timezone

logger = logging.getLogger('notifications')


class FCMService:
    """
    Serviço para envio de notificações via Firebase Cloud Messaging.
    """
    
    def __init__(self):
        self._messaging = None
        self._initialize()
    
    def _initialize(self):
        """Inicializa o cliente FCM."""
        try:
            from notifications.config import get_firebase_app
            
            app = get_firebase_app()
            if app:
                from firebase_admin import messaging
                self._messaging = messaging
                logger.info('FCM Service inicializado com sucesso')
            else:
                logger.warning('FCM Service não configurado - Firebase não disponível')
        except ImportError as e:
            logger.error(f'Erro ao importar firebase_admin: {e}')
        except Exception as e:
            logger.error(f'Erro ao inicializar FCM Service: {e}')
    
    def is_available(self) -> bool:
        """
        Verifica se o serviço FCM está disponível.
        
        Returns:
            bool: True se disponível, False caso contrário.
        """
        return self._messaging is not None
    
    def send_to_device(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Envia notificação para um único dispositivo.
        
        Args:
            token: Token do dispositivo.
            title: Título da notificação.
            body: Corpo da notificação.
            data: Dados adicionais (opcional).
            **kwargs: Argumentos adicionais para o FCM.
        
        Returns:
            dict: Resultado do envio com 'success', 'message_id' e 'error'.
        """
        if not self.is_available():
            logger.warning(f'FCM não disponível. Notificação simulada para: {token[:20]}...')
            return {
                'success': True,
                'message_id': 'mock-' + timezone.now().isoformat(),
                'error': None,
                'mock': True
            }
        
        try:
            # Construir mensagem
            message = self._build_message(token, title, body, data, **kwargs)
            
            # Enviar mensagem
            response = self._messaging.send(message)
            
            logger.info(f'Notificação enviada com sucesso: {response}')
            
            return {
                'success': True,
                'message_id': response,
                'error': None,
                'mock': False
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f'Erro ao enviar notificação: {error_msg}')
            
            return {
                'success': False,
                'message_id': None,
                'error': error_msg,
                'mock': False
            }
    
    def send_to_devices(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Envia notificação para múltiplos dispositivos.
        
        Args:
            tokens: Lista de tokens dos dispositivos.
            title: Título da notificação.
            body: Corpo da notificação.
            data: Dados adicionais (opcional).
            **kwargs: Argumentos adicionais para o FCM.
        
        Returns:
            dict: Resultado do envio com 'success_count', 'failure_count' e 'errors'.
        """
        if not self.is_available():
            logger.warning(f'FCM não disponível. Notificação simulada para {len(tokens)} dispositivos.')
            return {
                'success_count': len(tokens),
                'failure_count': 0,
                'errors': [],
                'mock': True
            }
        
        # FCM suporta até 500 tokens por requisição
        BATCH_SIZE = 500
        
        all_results = {
            'success_count': 0,
            'failure_count': 0,
            'errors': [],
            'mock': False
        }
        
        # Processar em batches
        for i in range(0, len(tokens), BATCH_SIZE):
            batch_tokens = tokens[i:i + BATCH_SIZE]
            
            try:
                # Construir mensagem multicast
                message = self._build_multicast_message(batch_tokens, title, body, data, **kwargs)
                
                # Enviar mensagem multicast
                response = self._messaging.send_each_for_multicast(message)
                
                all_results['success_count'] += response.success_count
                all_results['failure_count'] += response.failure_count
                
                # Coletar erros
                for idx, result in enumerate(response.responses):
                    if not result.success:
                        all_results['errors'].append({
                            'token': batch_tokens[idx],
                            'error': str(result.exception) if result.exception else 'Unknown error'
                        })
                
            except Exception as e:
                logger.error(f'Erro ao enviar batch: {e}')
                all_results['failure_count'] += len(batch_tokens)
                all_results['errors'].append({
                    'tokens': batch_tokens,
                    'error': str(e)
                })
        
        logger.info(
            f'Envio em massa concluído: {all_results["success_count"]} sucesso, '
            f'{all_results["failure_count"]} falhas'
        )
        
        return all_results
    
    def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Envia notificação para um tópico.
        
        Args:
            topic: Nome do tópico.
            title: Título da notificação.
            body: Corpo da notificação.
            data: Dados adicionais (opcional).
            **kwargs: Argumentos adicionais para o FCM.
        
        Returns:
            dict: Resultado do envio.
        """
        if not self.is_available():
            logger.warning(f'FCM não disponível. Notificação simulada para tópico: {topic}')
            return {
                'success': True,
                'message_id': 'mock-' + timezone.now().isoformat(),
                'error': None,
                'mock': True
            }
        
        try:
            message = self._build_message(
                token=None,
                topic=topic,
                title=title,
                body=body,
                data=data,
                **kwargs
            )
            
            response = self._messaging.send(message)
            
            logger.info(f'Notificação para tópico enviada: {topic} -> {response}')
            
            return {
                'success': True,
                'message_id': response,
                'error': None,
                'mock': False
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f'Erro ao enviar para tópico {topic}: {error_msg}')
            
            return {
                'success': False,
                'message_id': None,
                'error': error_msg,
                'mock': False
            }
    
    def send_broadcast(
        self,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Envia notificação broadcast para todos os dispositivos.
        
        Usa o tópico especial 'all' ou envia para todos os tokens ativos.
        
        Args:
            title: Título da notificação.
            body: Corpo da notificação.
            data: Dados adicionais (opcional).
            **kwargs: Argumentos adicionais para o FCM.
        
        Returns:
            dict: Resultado do envio.
        """
        # Enviar para tópico 'all' (requer subscrição prévia dos dispositivos)
        return self.send_to_topic('all', title, body, data, **kwargs)
    
    def _build_message(
        self,
        token: Optional[str] = None,
        topic: Optional[str] = None,
        title: str = '',
        body: str = '',
        data: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Any:
        """
        Constrói uma mensagem FCM.
        
        Args:
            token: Token do dispositivo (opcional).
            topic: Tópico (opcional).
            title: Título da notificação.
            body: Corpo da notificação.
            data: Dados adicionais.
            **kwargs: Argumentos adicionais.
        
        Returns:
            firebase_admin.messaging.Message: Mensagem FCM.
        """
        from firebase_admin import messaging
        
        # Construir payload
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data or {},
            android=self._build_android_config(**kwargs),
            apns=self._build_apns_config(title, body, **kwargs),
        )
        
        # Definir destinatário
        if token:
            message.token = token
        elif topic:
            message.topic = topic
        
        return message
    
    def _build_android_config(self, **kwargs) -> Any:
        """
        Constrói configuração específica para Android.
        
        Returns:
            firebase_admin.messaging.AndroidConfig: Configuração Android.
        """
        from firebase_admin import messaging
        
        return messaging.AndroidConfig(
            priority='high',
            ttl=kwargs.get('ttl', 3600),
            notification=messaging.AndroidNotification(
                sound=kwargs.get('sound', 'default'),
                color=kwargs.get('color', '#4CAF50'),
            )
        )
    
    def _build_apns_config(
        self,
        title: str,
        body: str,
        **kwargs
    ) -> Any:
        """
        Constrói configuração específica para iOS (APNS).
        
        Args:
            title: Título da notificação.
            body: Corpo da notificação.
            **kwargs: Argumentos adicionais.
        
        Returns:
            firebase_admin.messaging.APNSConfig: Configuração APNS.
        """
        from firebase_admin import messaging
        
        return messaging.APNSConfig(
            headers={
                'apns-priority': '10',
            },
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    alert=messaging.ApsAlert(
                        title=title,
                        body=body
                    ),
                    sound=kwargs.get('sound', 'default'),
                    badge=kwargs.get('badge', None),
                    content_available=kwargs.get('content_available', False),
                ),
            ),
        )


# Instância singleton do serviço
fcm_service = FCMService()
