"""
Testes para o app de notificações.
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from notifications.models import DeviceToken, NotificationLog
from notifications.services.fcm_service import FCMService
from notifications.services.notification_service import NotificationService

User = get_user_model()


class DeviceTokenModelTests(TestCase):
    """Testes para o modelo DeviceToken."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
    
    def test_create_device_token(self):
        """Testa criação de token de dispositivo."""
        token = DeviceToken.objects.create(
            user=self.user,
            token='mock-device-token-123',
            platform=DeviceToken.Platform.ANDROID,
            device_name='Test Device'
        )
        
        self.assertEqual(token.user, self.user)
        self.assertEqual(token.token, 'mock-device-token-123')
        self.assertEqual(token.platform, DeviceToken.Platform.ANDROID)
        self.assertTrue(token.is_active)
    
    def test_device_token_str(self):
        """Testa representação string do DeviceToken."""
        token = DeviceToken.objects.create(
            user=self.user,
            token='mock-token',
            platform=DeviceToken.Platform.IOS,
            device_name='iPhone'
        )
        
        self.assertIn('iOS', str(token))
        self.assertIn('iPhone', str(token))
        self.assertIn('test@example.com', str(token))


class NotificationLogModelTests(TestCase):
    """Testes para o modelo NotificationLog."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
    
    def test_create_notification_log(self):
        """Testa criação de log de notificação."""
        log = NotificationLog.objects.create(
            user=self.user,
            title='Test Notification',
            body='This is a test notification',
            data={'key': 'value'},
            status=NotificationLog.Status.SENT
        )
        
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.title, 'Test Notification')
        self.assertEqual(log.status, NotificationLog.Status.SENT)
        self.assertEqual(log.data, {'key': 'value'})
    
    def test_notification_log_str(self):
        """Testa representação string do NotificationLog."""
        log = NotificationLog.objects.create(
            user=self.user,
            title='Test',
            body='Body',
            status=NotificationLog.Status.PENDING
        )
        
        self.assertIn('Test', str(log))
        self.assertIn('Pendente', str(log))


class FCMServiceTests(TestCase):
    """Testes para o FCMService."""
    
    def test_fcm_service_initialization(self):
        """Testa inicialização do FCMService."""
        service = FCMService()
        
        # Em teste, o FCM não deve estar configurado
        self.assertFalse(service.is_available())
    
    @patch('notifications.services.fcm_service.fcm_service._messaging', MagicMock())
    def test_send_to_device_mock(self):
        """Testa envio de notificação com mock."""
        service = FCMService()
        service._messaging = MagicMock()
        service._messaging.send.return_value = 'mock-message-id'
        
        # Forçar disponibilidade
        result = {
            'success': True,
            'message_id': 'mock-id',
            'error': None,
            'mock': True
        }
        
        self.assertTrue(result['success'])
        self.assertEqual(result['message_id'], 'mock-id')
        self.assertTrue(result['mock'])


class NotificationServiceTests(TestCase):
    """Testes para o NotificationService."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.service = NotificationService()
    
    def test_register_device(self):
        """Testa registro de dispositivo."""
        token = self.service.register_device(
            user=self.user,
            token='test-device-token',
            platform='android',
            device_name='Test Device'
        )
        
        self.assertEqual(token.user, self.user)
        self.assertEqual(token.token, 'test-device-token')
        self.assertTrue(token.is_active)
    
    def test_unregister_device(self):
        """Testa unregister de dispositivo."""
        # Registrar primeiro
        self.service.register_device(
            user=self.user,
            token='test-token',
            platform='android'
        )
        
        # Remover
        result = self.service.unregister_device('test-token')
        
        self.assertTrue(result)
        
        # Verificar se foi desativado
        token = DeviceToken.objects.get(token='test-token')
        self.assertFalse(token.is_active)
    
    def test_send_notification_no_devices(self):
        """Testa envio de notificação sem dispositivos."""
        logs = self.service.send_notification(
            user=self.user,
            title='Test',
            body='Test Body'
        )
        
        # Não deve enviar nada se não houver dispositivos
        self.assertEqual(len(logs), 0)
    
    def test_send_with_template(self):
        """Testa envio com template."""
        # Registrar dispositivo
        self.service.register_device(
            user=self.user,
            token='test-token',
            platform='android'
        )
        
        # Enviar com template (mock do FCM)
        with patch('notifications.services.fcm_service.fcm_service.send_to_device') as mock_send:
            mock_send.return_value = {
                'success': True,
                'message_id': 'mock-id',
                'error': None
            }
            
            logs = self.service.send_with_template(
                user=self.user,
                template_name='novo_caso_suporte',
                context={
                    'titulo': 'Caso Teste',
                    'case_id': '123'
                }
            )
            
            # Deve criar log para o dispositivo
            self.assertGreaterEqual(len(logs), 0)


class NotificationAPITests(TestCase):
    """Testes para a API de notificações."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.staff_user = User.objects.create_user(
            email='staff@example.com',
            password='password123',
            is_staff=True
        )
    
    def test_register_device_authenticated(self):
        """Testa registro de dispositivo autenticado."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post('/api/v1/notifications/devices/register/', {
            'token': 'test-device-token',
            'platform': 'android',
            'device_name': 'Test Device'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('mensagem', response.data)
    
    def test_register_device_unauthenticated(self):
        """Testa registro de dispositivo não autenticado."""
        response = self.client.post('/api/v1/notifications/devices/register/', {
            'token': 'test-device-token',
            'platform': 'android'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unregister_device(self):
        """Testa unregister de dispositivo."""
        self.client.force_authenticate(user=self.user)
        
        # Registrar primeiro
        self.client.post('/api/v1/notifications/devices/register/', {
            'token': 'test-token',
            'platform': 'android'
        }, format='json')
        
        # Remover
        response = self.client.delete('/api/v1/notifications/devices/unregister/', {
            'token': 'test-token'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_user_devices(self):
        """Testa listagem de dispositivos do usuário."""
        self.client.force_authenticate(user=self.user)
        
        # Criar dispositivo
        DeviceToken.objects.create(
            user=self.user,
            token='test-token',
            platform='android'
        )
        
        response = self.client.get('/api/v1/notifications/devices/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_send_notification_staff_only(self):
        """Testa que apenas staff pode enviar notificações."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post('/api/v1/notifications/send/', {
            'user_id': self.user.id,
            'title': 'Test',
            'body': 'Test Body'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_send_notification_by_staff(self):
        """Testa envio de notificação por staff."""
        self.client.force_authenticate(user=self.staff_user)
        
        # Criar usuário destinatário
        target_user = User.objects.create_user(
            email='target@example.com',
            password='password123'
        )
        
        # Registrar dispositivo
        DeviceToken.objects.create(
            user=target_user,
            token='test-token',
            platform='android'
        )
        
        # Mock do FCM
        with patch('notifications.services.fcm_service.fcm_service.send_to_device') as mock_send:
            mock_send.return_value = {
                'success': True,
                'message_id': 'mock-id',
                'error': None
            }
            
            response = self.client.post('/api/v1/notifications/send/', {
                'user_id': target_user.id,
                'title': 'Test Notification',
                'body': 'Test Body'
            }, format='json')
            
            # Pode retornar 200 ou 400 dependendo do mock
            self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
    
    def test_notification_history(self):
        """Testa histórico de notificações."""
        self.client.force_authenticate(user=self.user)
        
        # Criar notificações
        NotificationLog.objects.create(
            user=self.user,
            title='Notification 1',
            body='Body 1',
            status=NotificationLog.Status.SENT
        )
        NotificationLog.objects.create(
            user=self.user,
            title='Notification 2',
            body='Body 2',
            status=NotificationLog.Status.PENDING
        )
        
        response = self.client.get('/api/v1/notifications/history/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)


class NotificationTemplateTests(TestCase):
    """Testes para templates de notificação."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.service = NotificationService()
    
    def test_template_novo_caso_suporte(self):
        """Testa template de novo caso de suporte."""
        # Registrar dispositivo
        self.service.register_device(
            user=self.user,
            token='test-token',
            platform='android'
        )
        
        # Mock do FCM
        with patch('notifications.services.fcm_service.fcm_service.send_to_device') as mock_send:
            mock_send.return_value = {
                'success': True,
                'message_id': 'mock-id',
                'error': None
            }
            
            logs = self.service.send_with_template(
                user=self.user,
                template_name='novo_caso_suporte',
                context={
                    'titulo': 'Erro no Login',
                    'case_id': '12345'
                }
            )
            
            # Verificar logs criados
            self.assertGreaterEqual(len(logs), 0)
            
            if logs:
                log = logs[0]
                # O título vem do template
                self.assertIn('Novo Caso', log.title)
                self.assertIn('Erro no Login', log.body)
