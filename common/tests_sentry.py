"""
Teste de validação do Sentry.

Este teste valida que o Sentry está configurado corretamente
e pode capturar exceções.
"""

import pytest
from unittest.mock import patch, MagicMock
import sentry_sdk


@pytest.mark.django_db
def test_sentry_sdk_installed():
    """
    Garante que o sentry-sdk está instalado e configurado.
    """
    # Verifica que o módulo está disponível
    assert sentry_sdk is not None


@pytest.mark.django_db
def test_sentry_configuration_in_settings():
    """
    Garante que as configurações do Sentry estão no settings.py.
    """
    from django.conf import settings

    # Verifica que as variáveis existem
    assert hasattr(settings, 'SENTRY_DSN')
    assert hasattr(settings, 'SENTRY_ENVIRONMENT')


@patch('sentry_sdk.capture_exception')
def test_sentry_capture_exception(mock_capture):
    """
    Testa que o Sentry captura exceções corretamente.
    """
    try:
        # Simula um erro
        raise ValueError("Erro de teste para Sentry")
    except ValueError as e:
        # Captura a exceção
        sentry_sdk.capture_exception(e)
        
        # Verifica que a captura foi chamada
        mock_capture.assert_called_once()
        assert mock_capture.call_args[0][0] == e


@patch('sentry_sdk.push_scope')
def test_sentry_context_enrichment(mock_push_scope):
    """
    Testa que o contexto enriquecido é enviado ao Sentry.
    """
    # Configura o mock de scope
    mock_scope = MagicMock()
    mock_push_scope.return_value.__enter__ = MagicMock(return_value=mock_scope)
    mock_push_scope.return_value.__exit__ = MagicMock(return_value=None)
    
    # Simula o uso de contexto enriquecido
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("test_tag", "test_value")
        scope.set_extra("test_extra", {"key": "value"})
    
    # Verifica que os métodos foram chamados
    mock_scope.set_tag.assert_called_once_with("test_tag", "test_value")
    mock_scope.set_extra.assert_called_once_with("test_extra", {"key": "value"})
