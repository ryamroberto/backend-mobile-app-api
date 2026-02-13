from django.db.models import QuerySet, Q
from ..models import ResolveCase
from users.models import User

def case_list_for_user(*, user: User) -> QuerySet[ResolveCase]:
    """
    Retorna os casos de suporte. 
    Usuários comuns veem apenas os seus. Staff vê todos.
    """
    if user.is_staff:
        return ResolveCase.objects.all()
    return ResolveCase.objects.filter(requester=user)

def case_get_by_id(*, user: User, case_id: str) -> ResolveCase:
    """
    Obtém um caso específico validando permissão de acesso.
    """
    if user.is_staff:
        return ResolveCase.objects.get(id=case_id)
    return ResolveCase.objects.get(id=case_id, requester=user)
