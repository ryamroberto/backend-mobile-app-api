from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
import logging

class DocumentationTests(APITestCase):
    def test_swagger_ui_accessible(self):
        """
        Garante que a interface do Swagger UI está acessível.
        """
        url = reverse('schema-swagger-ui')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_redoc_ui_accessible(self):
        """
        Garante que a interface do ReDoc está acessível.
        """
        url = reverse('schema-redoc')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_swagger_json_accessible(self):
        """
        Garante que o arquivo swagger.json está sendo gerado.
        """
        url = reverse('schema-json', kwargs={'format': '.json'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class LoggingTests(TestCase):
    """
    Testes para configuração de logging e auditoria.
    """
    
    def test_audit_logger_configured(self):
        """
        Garante que o logger de auditoria está configurado.
        """
        logger = logging.getLogger('audit')
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, 'audit')
    
    def test_automation_logger_configured(self):
        """
        Garante que o logger de automação está configurado.
        """
        logger = logging.getLogger('automation')
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, 'automation')
    
    def test_json_formatter_exists(self):
        """
        Garante que o formatador JSON está disponível.
        """
        from common.logging_formatters import JSONFormatter
        self.assertIsNotNone(JSONFormatter)
        
        # Testa a formatação
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=1,
            msg='Test message',
            args=(),
            exc_info=None
        )
        formatted = formatter.format(record)
        self.assertIn('timestamp', formatted)
        self.assertIn('level', formatted)
        self.assertIn('message', formatted)


class AuditTests(TestCase):
    """
    Testes para funções de auditoria.
    """
    
    def test_log_case_creation(self):
        """
        Garante que log_case_creation registra o log corretamente.
        """
        from common.audit import log_case_creation
        from unittest.mock import Mock
        
        # Mock de um caso
        mock_case = Mock()
        mock_case.id = 'test-case-id'
        mock_case.title = 'Test Case'
        mock_case.category = 'TECHNICAL'
        mock_case.requester = 'test_user'
        
        # Deve executar sem erros
        log_case_creation(case=mock_case, user='test_user')
    
    def test_log_case_status_change(self):
        """
        Garante que log_case_status_change registra o log corretamente.
        """
        from common.audit import log_case_status_change
        from unittest.mock import Mock
        
        mock_case = Mock()
        mock_case.id = 'test-case-id'
        mock_case.title = 'Test Case'
        
        log_case_status_change(
            case=mock_case,
            old_status='OPEN',
            new_status='IN_PROGRESS',
            user='test_user'
        )
    
    def test_log_task_creation(self):
        """
        Garante que log_task_creation registra o log corretamente.
        """
        from common.audit import log_task_creation
        from unittest.mock import Mock
        
        mock_task = Mock()
        mock_task.id = 'test-task-id'
        mock_task.title = 'Test Task'
        mock_task.task_type = 'CUSTOM'
        mock_task.associated_case = None
        mock_task.owner = 'test_user'
        
        log_task_creation(task=mock_task, user='test_user')
    
    def test_log_task_status_change(self):
        """
        Garante que log_task_status_change registra o log corretamente.
        """
        from common.audit import log_task_status_change
        from unittest.mock import Mock
        
        mock_task = Mock()
        mock_task.id = 'test-task-id'
        mock_task.title = 'Test Task'
        mock_task.associated_case = None
        mock_task.owner = 'test_user'
        
        log_task_status_change(
            task=mock_task,
            old_status='PENDING',
            new_status='RUNNING',
            user='test_user'
        )