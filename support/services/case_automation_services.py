import logging
import sentry_sdk
from django.apps import apps
from importlib import import_module
from ..models import ResolveCase

logger = logging.getLogger('automation')

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

        # Log de auditoria: início da automação
        logger.info(
            f"Iniciando automação para caso {case.id}",
            extra={
                'case_id': str(case.id),
                'case_title': case.title,
                'case_category': case.category,
                'requester': case.requester,
                'action': 'automation_triggered'
            }
        )

        # Cria a tarefa de automação via Service Layer
        task = task_create(
            user=case.requester,
            title=f"Automação para Caso #{case.id}: {case.title}",
            description=f"Tarefa disparada automaticamente para o caso: {case.description}",
            task_type=task_type,
            provider_id="AUTO-RESOLVE-AI-AGENT",
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

        # Log de auditoria: automação concluída com sucesso
        logger.info(
            f"Automação concluída com sucesso para caso {case.id}",
            extra={
                'case_id': str(case.id),
                'task_id': task.id if task else None,
                'action': 'automation_completed'
            }
        )

        return task

    except (LookupError, ImportError, Exception) as e:
        # AC4: Não causa falha no fluxo se appdata estiver indisponível ou ocorrer erro
        # Captura contexto enriquecido no Sentry
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("automation_error", True)
            scope.set_extra("case_id", str(case.id))
            scope.set_extra("case_title", case.title)
            scope.set_extra("case_category", case.category)
            scope.set_extra("requester", str(case.requester))
            scope.set_extra("error_type", type(e).__name__)
            sentry_sdk.capture_exception(e)

        logger.error(
            f"Falha ao disparar automação para caso {case.id}: {str(e)}",
            extra={
                'case_id': str(case.id),
                'case_title': case.title,
                'case_category': case.category,
                'error_type': type(e).__name__,
                'action': 'automation_failed'
            },
            exc_info=True
        )
        return None
