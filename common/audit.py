"""
Módulo de auditoria para registro de ações críticas no sistema.

Este módulo fornece funções utilitárias para log de auditoria de:
- Criação de casos de suporte
- Alteração de status de tarefas
- Ações administrativas críticas

Os logs são estruturados em JSON e enviados para:
- Console (em desenvolvimento)
- Arquivo (em produção)
- Sentry (apenas erros)
"""

import logging
from typing import Optional, Any, Dict

logger = logging.getLogger('audit')


def log_case_creation(case, user: Any = None):
    """
    Registra a criação de um novo caso de suporte.
    
    Args:
        case: Instância do caso criado (ResolveCase)
        user: Usuário que criou o caso (opcional, pode ser extraído do case)
    """
    user = user or getattr(case, 'requester', None)
    
    logger.info(
        f"Caso de suporte criado: {case.id}",
        extra={
            'action': 'case_created',
            'case_id': str(case.id),
            'case_title': case.title,
            'case_category': case.category if hasattr(case, 'category') else None,
            'user': str(user) if user else 'unknown',
            'audit_type': 'case_management'
        }
    )


def log_case_status_change(case, old_status: str, new_status: str, user: Any = None):
    """
    Registra a alteração de status de um caso.
    
    Args:
        case: Instância do caso (ResolveCase)
        old_status: Status anterior
        new_status: Novo status
        user: Usuário que fez a alteração
    """
    logger.info(
        f"Status do caso {case.id} alterado de {old_status} para {new_status}",
        extra={
            'action': 'case_status_changed',
            'case_id': str(case.id),
            'case_title': case.title,
            'old_status': old_status,
            'new_status': new_status,
            'user': str(user) if user else 'unknown',
            'audit_type': 'case_management'
        }
    )


def log_task_status_change(task, old_status: str, new_status: str, user: Any = None):
    """
    Registra a alteração de status de uma tarefa de automação.
    
    Args:
        task: Instância da tarefa (AutomationTask)
        old_status: Status anterior
        new_status: Novo status
        user: Usuário que fez a alteração
    """
    logger.info(
        f"Status da tarefa {task.id} alterado de {old_status} para {new_status}",
        extra={
            'action': 'task_status_changed',
            'task_id': str(task.id),
            'task_title': task.title,
            'old_status': old_status,
            'new_status': new_status,
            'associated_case': str(task.associated_case.id) if task.associated_case else None,
            'user': str(user) if user else 'unknown',
            'audit_type': 'automation'
        }
    )


def log_task_creation(task, user: Any = None):
    """
    Registra a criação de uma nova tarefa de automação.
    
    Args:
        task: Instância da tarefa criada (AutomationTask)
        user: Usuário que criou a tarefa
    """
    user = user or getattr(task, 'owner', None)
    
    logger.info(
        f"Tarefa de automação criada: {task.id}",
        extra={
            'action': 'task_created',
            'task_id': str(task.id),
            'task_title': task.title,
            'task_type': task.task_type if hasattr(task, 'task_type') else None,
            'associated_case': str(task.associated_case.id) if task.associated_case else None,
            'user': str(user) if user else 'unknown',
            'audit_type': 'automation'
        }
    )


def log_admin_action(action: str, details: Optional[Dict[str, Any]] = None, user: Any = None):
    """
    Registra uma ação administrativa genérica.
    
    Args:
        action: Nome/descrição da ação
        details: Dicionário com detalhes adicionais da ação
        user: Usuário que realizou a ação
    """
    extra_data: Dict[str, Any] = {
        'action': action,
        'user': str(user) if user else 'unknown',
        'audit_type': 'admin'
    }
    
    if details:
        extra_data.update(details)
    
    logger.info(
        f"Ação administrativa: {action}",
        extra=extra_data
    )


def log_error_audit(error: Exception, context: Optional[Dict[str, Any]] = None, user: Any = None):
    """
    Registra um erro em contexto de auditoria.
    
    Args:
        error: Exceção ocorrida
        context: Contexto adicional sobre o erro
        user: Usuário afetado pelo erro
    """
    extra_data: Dict[str, Any] = {
        'action': 'audit_error',
        'error_type': type(error).__name__,
        'user': str(user) if user else 'unknown',
        'audit_type': 'error'
    }
    
    if context:
        extra_data.update(context)
    
    logger.error(
        f"Erro em ação de auditoria: {str(error)}",
        extra=extra_data,
        exc_info=True
    )
