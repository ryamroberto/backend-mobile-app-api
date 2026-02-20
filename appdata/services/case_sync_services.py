from django.apps import apps

def sync_task_result_to_case(*, task):
    """
    Sincroniza os resultados de uma AutomationTask de volta para o ResolveCase associado.
    """
    if not task.associated_case:
        return

    case = task.associated_case
    AutomationTask = apps.get_model('appdata', 'AutomationTask')
    ResolveCase = apps.get_model('support', 'ResolveCase')

    if task.execution_status == AutomationTask.ExecutionStatus.COMPLETED:
        case.status = ResolveCase.Status.RESOLVED
        case.resolution_notes = f"""Resolução Automática via Tarefa #{task.id}:
{task.output_results}"""
    
    elif task.execution_status == AutomationTask.ExecutionStatus.FAILED:
        # Caso falhe, mantemos em IN_PROGRESS e anexamos o erro para análise humana
        case.resolution_notes = f"""Falha na Automação #{task.id}:
{task.output_results.get('error', 'Erro desconhecido')}"""
        # Status permanece IN_PROGRESS conforme critério 3.2

    case.save(update_fields=['status', 'resolution_notes'])
