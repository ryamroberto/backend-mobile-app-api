import logging
from django.apps import apps
from importlib import import_module
from ..models import ResolveCase

logger = logging.getLogger(__name__)

def trigger_case_automation(*, case: ResolveCase):
    """
    Orquestra a criação de uma AutomationTask baseada na categoria do caso.
    Garante que falhas na automação não quebrem o fluxo principal (AC4).
    """
    if case.category not in [ResolveCase.Category.TECHNICAL, ResolveCase.Category.AI_REFINEMENT]:
        return None

    try:
        AutomationTask = apps.get_model('appdata', 'AutomationTask')
        resource_services = import_module('appdata.services.resource_services')
        task_create = resource_services.task_create
        
        # Define o tipo de tarefa baseado na categoria
        task_type = AutomationTask.TaskType.CUSTOM
        if case.category == ResolveCase.Category.AI_REFINEMENT:
            task_type = AutomationTask.TaskType.BEDROCK
        
        # Cria a tarefa de automação via Service Layer
        task = task_create(
            user=case.requester,
            title=f"Automação para Caso #{case.id}: {case.title}",
            description=f"Tarefa disparada automaticamente para o caso: {case.description}",
            task_type=task_type,
            provider_id="AUTO-RESOLVE-AI-AGENT", # Default para automação
            associated_case=case,
            execution_status=AutomationTask.ExecutionStatus.PENDING,
            input_params={
                'case_id': str(case.id),
                'case_title': case.title,
                'case_category': case.category,
            }
        )
        
        # Atualiza o status do caso para EM ANDAMENTO
        case.status = ResolveCase.Status.IN_PROGRESS
        case.save(update_fields=['status'])
        
        return task

    except (LookupError, ImportError, Exception) as e:
        # AC4: Não causa falha no fluxo se appdata estiver indisponível ou ocorrer erro
        logger.error(f"Falha ao disparar automação para o caso {case.id}: {str(e)}")
        return None
