from typing import Any, Dict
from django.db import transaction
from ..models import ResolveCase
from users.models import User

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
    case.resolution_notes = resolution_notes
    case.status = status
    case.full_clean()
    case.save()
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
    update_fields = ['title', 'description', 'category', 'status']
    for field in update_fields:
        if field in data:
            setattr(case, field, data[field])
    
    case.full_clean()
    case.save()
    return case
