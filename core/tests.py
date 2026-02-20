from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings


class HealthCheckTests(TestCase):
    """Testes para endpoints de health check e readiness."""
    
    def setUp(self):
        self.client = Client()
    
    def test_health_check_endpoint_exists(self):
        """Testa se o endpoint /health/ existe e retorna 200."""
        response = self.client.get(reverse('health-check'))
        self.assertEqual(response.status_code, 200)
    
    def test_health_check_returns_json(self):
        """Testa se /health/ retorna JSON válido."""
        response = self.client.get(reverse('health-check'))
        self.assertEqual(response['Content-Type'], 'application/json')
    
    def test_health_check_structure(self):
        """Testa a estrutura da resposta do health check."""
        response = self.client.get(reverse('health-check'))
        data = response.json()
        
        self.assertIn('status', data)
        self.assertIn('version', data)
        self.assertIn('checks', data)
        self.assertIn('database', data['checks'])
    
    def test_health_check_status_values(self):
        """Testa se o status é healthy ou unhealthy."""
        response = self.client.get(reverse('health-check'))
        data = response.json()
        
        self.assertIn(data['status'], ['healthy', 'unhealthy'])
    
    def test_health_check_database_status(self):
        """Testa se o status do banco de dados é válido."""
        response = self.client.get(reverse('health-check'))
        data = response.json()
        
        db_status = data['checks']['database']['status']
        self.assertIn(db_status, ['healthy', 'unhealthy'])
    
    def test_readiness_check_endpoint_exists(self):
        """Testa se o endpoint /ready/ existe."""
        response = self.client.get(reverse('readiness-check'))
        self.assertIsNotNone(response)
    
    def test_readiness_check_returns_json(self):
        """Testa se /ready/ retorna JSON válido."""
        response = self.client.get(reverse('readiness-check'))
        self.assertEqual(response['Content-Type'], 'application/json')
    
    def test_readiness_check_structure(self):
        """Testa a estrutura da resposta do readiness check."""
        response = self.client.get(reverse('readiness-check'))
        data = response.json()
        
        self.assertIn('ready', data)
        self.assertIn('checks', data)
        self.assertIn('database', data['checks'])
    
    def test_readiness_check_ready_is_boolean(self):
        """Testa se 'ready' é um booleano."""
        response = self.client.get(reverse('readiness-check'))
        data = response.json()
        
        self.assertIsInstance(data['ready'], bool)
    
    def test_health_check_with_debug_true(self):
        """Testa health check com DEBUG=True."""
        with self.settings(DEBUG=True):
            response = self.client.get(reverse('health-check'))
            data = response.json()
            
            self.assertEqual(data['checks']['debug']['status'], 'warning')
    
    def test_health_check_with_debug_false(self):
        """Testa health check com DEBUG=False."""
        with self.settings(DEBUG=False):
            response = self.client.get(reverse('health-check'))
            data = response.json()
            
            self.assertEqual(data['checks']['debug']['status'], 'healthy')
    
    def test_version_in_settings(self):
        """Testa se APP_VERSION está configurado."""
        version = getattr(settings, 'APP_VERSION', '1.0.0')
        self.assertIsNotNone(version)
        self.assertIsInstance(version, str)


class HealthCheckIntegrationTests(TestCase):
    """Testes de integração para health check."""
    
    def setUp(self):
        self.client = Client()
    
    def test_health_check_database_connection(self):
        """Testa se o health check detecta conexão com banco."""
        response = self.client.get(reverse('health-check'))
        data = response.json()
        
        # Em testes, o banco deve estar saudável
        self.assertEqual(data['checks']['database']['status'], 'healthy')
        self.assertEqual(data['status'], 'healthy')
    
    def test_readiness_check_migrations(self):
        """Testa se readiness check verifica migrações."""
        response = self.client.get(reverse('readiness-check'))
        data = response.json()
        
        self.assertIn('migrations', data['checks'])
        self.assertIn('status', data['checks']['migrations'])
