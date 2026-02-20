from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from django.apps import apps
from importlib import import_module
from .models import ResolveCase
from .services.case_services import case_create

User = get_user_model()

class CaseAutomationIntegrationTests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='tester@example.com',
            password='password123'
        )
        self.AutomationTask = apps.get_model('appdata', 'AutomationTask')

    def test_automation_task_created_on_technical_case(self):
        """Garante que uma tarefa de automação é criada para casos técnicos."""
        case = case_create(
            user=self.user,
            title="Falha no Cluster",
            description="O cluster EKS não está respondendo.",
            category=ResolveCase.Category.TECHNICAL
        )
        
        # Verifica se o status mudou para IN_PROGRESS
        case.refresh_from_db()
        self.assertEqual(case.status, ResolveCase.Status.IN_PROGRESS)
        
        # Verifica se a AutomationTask foi criada
        task = self.AutomationTask.objects.filter(associated_case=case).first()
        self.assertIsNotNone(task)
        self.assertEqual(task.task_type, self.AutomationTask.TaskType.CUSTOM)
        self.assertEqual(task.owner, self.user)

    def test_automation_task_created_on_ai_refinement_case(self):
        """Garante que uma tarefa Bedrock é criada para refinamento de IA."""
        case = case_create(
            user=self.user,
            title="Refinar Modelo",
            description="Aumentar a precisão do agente.",
            category=ResolveCase.Category.AI_REFINEMENT
        )
        
        task = self.AutomationTask.objects.filter(associated_case=case).first()
        self.assertIsNotNone(task)
        self.assertEqual(task.task_type, self.AutomationTask.TaskType.BEDROCK)

    def test_no_automation_on_billing_case(self):
        """Garante que casos de faturamento não disparam automação."""
        case = case_create(
            user=self.user,
            title="Erro na fatura",
            description="Cobrança duplicada.",
            category=ResolveCase.Category.BILLING
        )
        
        # Status deve permanecer OPEN
        case.refresh_from_db()
        self.assertEqual(case.status, ResolveCase.Status.OPEN)
        
        # Nenhuma tarefa deve ser criada
        self.assertEqual(self.AutomationTask.objects.filter(associated_case=case).count(), 0)

    def test_sync_task_completion_to_case(self):
        """Garante que a conclusão da tarefa resolve o caso."""
        case = case_create(
            user=self.user,
            title="Fix Bug",
            description="Bug description",
            category=ResolveCase.Category.TECHNICAL
        )
        
        task = self.AutomationTask.objects.get(associated_case=case)
        
        # Simula conclusão da tarefa via Service
        resource_services = import_module('appdata.services.resource_services')
        task_update = resource_services.task_update
        task_update(
            task=task,
            execution_status=self.AutomationTask.ExecutionStatus.COMPLETED,
            output_results={'status': 'success', 'message': 'Corrigido automaticamente.'}
        )
        
        case.refresh_from_db()
        self.assertEqual(case.status, ResolveCase.Status.RESOLVED)
        self.assertIn("Resolução Automática", case.resolution_notes)
        self.assertIn("Corrigido automaticamente", case.resolution_notes)

    def test_sync_task_failure_to_case(self):
        """Garante que a falha da tarefa registra o erro no caso."""
        case = case_create(
            user=self.user,
            title="Fix Bug",
            description="Bug description",
            category=ResolveCase.Category.TECHNICAL
        )
        
        task = self.AutomationTask.objects.get(associated_case=case)
        
        # Simula falha da tarefa
        resource_services = import_module('appdata.services.resource_services')
        task_update = resource_services.task_update
        task_update(
            task=task,
            execution_status=self.AutomationTask.ExecutionStatus.FAILED,
            output_results={'error': 'Erro na conexão com o cluster.'}
        )
        
        case.refresh_from_db()
        # Permanece em IN_PROGRESS conforme critério 3.2
        self.assertEqual(case.status, ResolveCase.Status.IN_PROGRESS)
        self.assertIn("Falha na Automação", case.resolution_notes)
        self.assertIn("Erro na conexão", case.resolution_notes)

    def test_case_creation_does_not_fail_if_automation_fails(self):
        """Garante que o caso de suporte é criado mesmo se a automação falhar (AC4)."""
        from unittest.mock import patch
        
        # Simula erro crítico na automação (ex: erro de importação ou modelo ausente)
        with patch('support.services.case_automation_services.import_module', side_effect=ImportError("Appdata indisponível")):
            case = case_create(
                user=self.user,
                title="Caso Robusto",
                description="Este caso deve ser criado mesmo com erro na automação.",
                category=ResolveCase.Category.TECHNICAL
            )
            
            # O caso deve ser criado com sucesso
            self.assertIsNotNone(case.id)
            # Como a automação falhou, o status deve permanecer OPEN (ou não mudar para IN_PROGRESS)
            case.refresh_from_db()
            self.assertEqual(case.status, ResolveCase.Status.OPEN)
