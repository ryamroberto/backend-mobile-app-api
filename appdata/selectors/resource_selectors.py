from django.db.models import QuerySet
from ..models import AutomationTask
from users.models import User

def task_list_for_user(*, user: User) -> QuerySet[AutomationTask]:
    """
    Retorna a lista de tarefas de automação pertencentes a um usuário específico.
    """
    return AutomationTask.objects.filter(owner=user)

def task_get_by_id(*, user: User, task_id: str) -> AutomationTask:
    """
    Retorna uma tarefa específica pertencente a um usuário.
    """
    return AutomationTask.objects.get(owner=user, id=task_id)
