from typing import Any, Dict, Optional
from django.db import transaction
from ..models import AutomationTask
from users.models import User
from . import eks_services
from .case_sync_services import sync_task_result_to_case

@transaction.atomic
def task_create(
    *,
    user: User,
    title: str,
    description: str = "",
    task_type: str = AutomationTask.TaskType.CUSTOM,
    provider_id: str = "",
    input_params: Dict[str, Any] = None,
    execution_status: str = AutomationTask.ExecutionStatus.PENDING,
    associated_case: Optional[Any] = None
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
        execution_status=execution_status,
        associated_case=associated_case
    )
    task.full_clean()
    task.save()
    
    # Se a tarefa for criada já como RUNNING, executa
    if execution_status == AutomationTask.ExecutionStatus.RUNNING:
        _trigger_task_execution(task)
        
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
    old_status = task.execution_status
    
    update_fields = [
        'title', 'description', 'task_type', 'provider_id', 
        'execution_status', 'input_params', 'output_results',
        'associated_case'
    ]
    
    for field in update_fields:
        if field in data:
            setattr(task, field, data[field])
            
    task.full_clean()
    task.save()
    
    # Se o status mudou para RUNNING, dispara execução
    if old_status != AutomationTask.ExecutionStatus.RUNNING and \
       task.execution_status == AutomationTask.ExecutionStatus.RUNNING:
        _trigger_task_execution(task)
    
    # Se o status mudou para COMPLETED ou FAILED, sincroniza com o caso se houver
    if old_status != task.execution_status and \
       task.execution_status in [AutomationTask.ExecutionStatus.COMPLETED, AutomationTask.ExecutionStatus.FAILED]:
        sync_task_result_to_case(task=task)
    
    return task

def _trigger_task_execution(task: AutomationTask) -> None:
    """
    Lógica interna para disparar a execução baseada no tipo.
    """
    if task.task_type == AutomationTask.TaskType.EKS:
        yaml_manifest = task.input_params.get("yaml_manifest")
        namespace = task.input_params.get("namespace", "default")
        
        if not yaml_manifest:
            task.execution_status = AutomationTask.ExecutionStatus.FAILED
            task.output_results = {"error": "Manifest YAML não fornecido em input_params."}
            task.save()
            sync_task_result_to_case(task=task)
            return

        try:
            results = eks_services.task_execute_eks(
                yaml_manifest=yaml_manifest,
                namespace=namespace
            )
            task.output_results = {"applied_resources": results}
            task.execution_status = AutomationTask.ExecutionStatus.COMPLETED
        except Exception as e:
            task.execution_status = AutomationTask.ExecutionStatus.FAILED
            task.output_results = {"error": str(e)}
        
        task.save()
        sync_task_result_to_case(task=task)
    
    # Para CUSTOM e outros tipos que podem ser marcados como COMPLETED/FAILED manualmente
    # a sincronização é feita no task_update.

@transaction.atomic
def task_delete(*, task: AutomationTask) -> None:
    """
    Remove uma tarefa.
    """
    task.delete()
