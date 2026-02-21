"""
Configuração do Firebase Cloud Messaging (FCM) para notificações push.
"""
import os
import json
import logging

logger = logging.getLogger('notifications')

# Configuração do Firebase
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID')
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
FIREBASE_CREDENTIALS_JSON = os.getenv('FIREBASE_CREDENTIALS')

# Variável global para armazenar a aplicação Firebase
_firebase_app = None


def get_firebase_app():
    """
    Obtém ou inicializa a aplicação Firebase.
    
    Returns:
        firebase_admin.App: Aplicação Firebase inicializada ou None se não configurada.
    """
    global _firebase_app
    
    if _firebase_app is not None:
        return _firebase_app
    
    # Verificar se temos credenciais
    if not FIREBASE_PROJECT_ID:
        logger.warning('FIREBASE_PROJECT_ID não configurado. FCM desativado.')
        return None
    
    try:
        import firebase_admin
        from firebase_admin import credentials
        
        # Tentar carregar credenciais de diferentes fontes
        cred = None
        
        # 1. Tentar carregar de arquivo JSON
        if GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
            logger.info(f'Carregando credenciais Firebase de: {GOOGLE_APPLICATION_CREDENTIALS}')
            cred = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
        
        # 2. Tentar carregar de variável de ambiente JSON
        elif FIREBASE_CREDENTIALS_JSON:
            logger.info('Carregando credenciais Firebase de FIREBASE_CREDENTIALS')
            try:
                cred_dict = json.loads(FIREBASE_CREDENTIALS_JSON)
                cred = credentials.Certificate(cred_dict)
            except json.JSONDecodeError as e:
                logger.error(f'Erro ao parsear FIREBASE_CREDENTIALS: {e}')
                return None
        
        # 3. Usar credenciais padrão (Application Default Credentials)
        else:
            logger.info('Usando Application Default Credentials do Firebase')
            cred = credentials.ApplicationDefault()
        
        # Inicializar aplicação Firebase
        _firebase_app = firebase_admin.initialize_app(cred, {
            'projectId': FIREBASE_PROJECT_ID,
        })
        
        logger.info('Firebase Admin SDK inicializado com sucesso')
        return _firebase_app
        
    except ImportError:
        logger.error('firebase-admin não instalado. Execute: pip install firebase-admin')
        return None
    except Exception as e:
        logger.error(f'Erro ao inicializar Firebase: {e}')
        return None


def is_firebase_configured():
    """
    Verifica se o Firebase está configurado corretamente.
    
    Returns:
        bool: True se configurado, False caso contrário.
    """
    app = get_firebase_app()
    return app is not None
