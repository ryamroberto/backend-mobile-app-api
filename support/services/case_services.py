import logging
from django.db import transaction
from ..models import ResolveCase
from users.models import User
from .case_automation_services import trigger_case_automation
from common.audit import log_case_creation, log_case_status_change

logger = logging.getLogger('automation')

@transaction.atomic
def case_create(
    *,
    user: User,
    title: str,
    description: str,
    category: str = ResolveCase.Category.TECHNICAL
) -> ResolveCase:
    """
    Cria um novo caso de suporte.
    """
    case = ResolveCase(
        requester=user,
        title=title,
        description=description,
        category=category,
        status=ResolveCase.Status.OPEN
    )
    case.full_clean()
    case.save()

    # Log de auditoria: criação de caso
    log_case_creation(case=case, user=user)

    # Dispara automação após commit bem-sucedido (AC4: tratamento defensivo)
    def _safe_automation_trigger():
        """Wrapper defensivo para garantir que falhas na automação não quebrem o fluxo."""
        try:
            trigger_case_automation(case=case)
        except Exception as e:
            # AC4: Captura qualquer exceção residual e loga sem propagar
            logger.error(
                f"Falha residual na automação do caso {case.id}: {str(e)}",
                extra={
                    'case_id': str(case.id),
                    'case_title': case.title,
                    'error_type': type(e).__name__,
                    'action': 'automation_callback_failed'
                },
                exc_info=True
            )

    transaction.on_commit(_safe_automation_trigger)

    return case

@transaction.atomic
def case_resolve(
    *,
    case: ResolveCase,
    resolution_notes: str,
    status: str = ResolveCase.Status.RESOLVED
) -> ResolveCase:
    """
    Marca um caso como resolvido ou fechado com notas.
    """
    old_status = case.status
    
    case.resolution_notes = resolution_notes
    case.status = status
    case.full_clean()
    case.save()
    
    # Log de auditoria: alteração de status
    log_case_status_change(
        case=case,
        old_status=old_status,
        new_status=status,
        user=getattr(case, 'requester', None)
    )
    
    return case

@transaction.atomic
def case_update(
    *,
    case: ResolveCase,
    **data
) -> ResolveCase:
    """
    Atualiza dados básicos do caso.
    """
    old_status = case.status if 'status' in data else None
    
    update_fields = ['title', 'description', 'category', 'status']
    for field in update_fields:
        if field in data:
            setattr(case, field, data[field])

    case.full_clean()
    case.save()
    
    # Log de auditoria: alteração de status (se aplicável)
    if 'status' in data and old_status != data['status']:
        log_case_status_change(
            case=case,
            old_status=old_status,
            new_status=data['status'],
            user=getattr(case, 'requester', None)
        )
    
    return case
