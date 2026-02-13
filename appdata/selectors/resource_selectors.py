from django.db.models import QuerySet
from ..models import Resource
from users.models import User

def resource_list_for_user(*, user: User) -> QuerySet[Resource]:
    """
    Retorna a lista de recursos pertencentes a um usuário específico.
    """
    return Resource.objects.filter(owner=user)

def resource_get_by_id(*, user: User, resource_id: str) -> Resource:
    """
    Retorna um recurso específico pertencente a um usuário.
    Levanta Resource.DoesNotExist se não encontrado.
    """
    return Resource.objects.get(owner=user, id=resource_id)
