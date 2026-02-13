from typing import Any, Dict
from django.db import transaction
from ..models import AutomationTask
from users.models import User

@transaction.atomic
def task_create(
    *,
    user: User,
    title: str,
    description: str = "",
    task_type: str = AutomationTask.TaskType.CUSTOM,
    provider_id: str = "",
    input_params: Dict[str, Any] = None,
    execution_status: str = AutomationTask.ExecutionStatus.PENDING
) -> AutomationTask:
    """
    Cria uma nova tarefa de automação associada a um usuário.
    """
    if input_params is None:
        input_params = {}
        
    task = AutomationTask(
        owner=user,
        title=title,
        description=description,
        task_type=task_type,
        provider_id=provider_id,
        input_params=input_params,
        execution_status=execution_status
    )
    task.full_clean()
    task.save()
    
    return task

@transaction.atomic
def task_update(
    *,
    task: AutomationTask,
    **data
) -> AutomationTask:
    """
    Atualiza uma tarefa de automação existente.
    """
    update_fields = [
        'title', 'description', 'task_type', 'provider_id', 
        'execution_status', 'input_params', 'output_results'
    ]
    
    for field in update_fields:
        if field in data:
            setattr(task, field, data[field])
            
    task.full_clean()
    task.save()
    
    return task

@transaction.atomic
def task_delete(*, task: AutomationTask) -> None:
    """
    Remove uma tarefa.
    """
    task.delete()
