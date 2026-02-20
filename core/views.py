import logging
from django.http import JsonResponse
from django.db import connection
from django.conf import settings

logger = logging.getLogger('health')


def health_check(request):
    """
    Endpoint de health check para monitoramento e CI/CD.
    
    Retorna o status geral da aplicação e verificações de dependências.
    """
    health_status = {
        'status': 'healthy',
        'version': getattr(settings, 'APP_VERSION', '1.0.0'),
        'checks': {}
    }
    
    # Verificar banco de dados
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        health_status['checks']['database'] = {
            'status': 'healthy',
            'message': 'Banco de dados conectado'
        }
    except Exception as e:
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'message': str(e)
        }
        health_status['status'] = 'unhealthy'
    
    # Verificar se está em modo debug
    health_status['checks']['debug'] = {
        'status': 'warning' if settings.DEBUG else 'healthy',
        'message': 'DEBUG ativado' if settings.DEBUG else 'DEBUG desativado'
    }
    
    # Determinar status HTTP
    if health_status['status'] == 'healthy':
        status_code = 200
    elif any(c.get('status') == 'unhealthy' for c in health_status['checks'].values()):
        status_code = 503
    else:
        status_code = 200
    
    return JsonResponse(health_status, status=status_code)


def readiness_check(request):
    """
    Endpoint de readiness check para Kubernetes/orquestradores.
    
    Verifica se a aplicação está pronta para receber tráfego.
    """
    readiness_status = {
        'ready': True,
        'checks': {}
    }
    
    # Verificar migrations
    try:
        from django.db.migrations.executor import MigrationExecutor
        
        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        plan = executor.migration_plan(targets)
        
        # Verificar se há migrations pendentes
        pending_migrations = [
            migration for migration, backwards in plan
            if migration not in executor.applied_migrations
        ]
        
        if pending_migrations:
            readiness_status['ready'] = False
            readiness_status['checks']['migrations'] = {
                'status': 'pending',
                'message': f'{len(pending_migrations)} migrações pendentes'
            }
        else:
            readiness_status['checks']['migrations'] = {
                'status': 'ready',
                'message': 'Todas migrações aplicadas'
            }
    except Exception as e:
        readiness_status['ready'] = False
        readiness_status['checks']['migrations'] = {
            'status': 'error',
            'message': str(e)
        }
    
    # Verificar banco de dados
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        readiness_status['checks']['database'] = {
            'status': 'ready',
            'message': 'Banco de dados conectado'
        }
    except Exception as e:
        readiness_status['ready'] = False
        readiness_status['checks']['database'] = {
            'status': 'error',
            'message': str(e)
        }
    
    status_code = 200 if readiness_status['ready'] else 503
    return JsonResponse(readiness_status, status=status_code)
