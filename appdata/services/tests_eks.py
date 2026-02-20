from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.exceptions import ValidationError
from .eks_services import task_execute_eks

class EKSServiceTests(TestCase):
    
    @patch('appdata.services.eks_services.get_kubernetes_client')
    @patch('kubernetes.utils.create_from_dict')
    def test_task_execute_eks_success(self, mock_create, mock_get_client):
        """
        Garante que o serviço processa corretamente um manifest YAML válido.
        """
        mock_get_client.return_value = MagicMock()
        yaml_manifest = """
apiVersion: v1
kind: ConfigMap
metadata:
  name: test-config
data:
  key: value
"""
        results = task_execute_eks(yaml_manifest=yaml_manifest, namespace="test-ns")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["status"], "CREATED")
        self.assertEqual(results[0]["name"], "test-config")
        mock_create.assert_called_once()

    @patch('appdata.services.eks_services.get_kubernetes_client')
    def test_task_execute_eks_invalid_yaml(self, mock_get_client):
        """
        Garante que falha ao receber YAML inválido.
        """
        mock_get_client.return_value = MagicMock()
        with self.assertRaises(ValidationError) as cm:
            task_execute_eks(yaml_manifest="invalid: yaml: :")
        self.assertIn("Erro ao processar YAML", str(cm.exception))

    @patch('appdata.services.eks_services.get_kubernetes_client')
    def test_task_execute_eks_no_client(self, mock_get_client):
        """
        Garante que falha se não houver conexão com o cluster.
        """
        mock_get_client.return_value = None
        with self.assertRaises(ValidationError) as cm:
            task_execute_eks(yaml_manifest="kind: Pod")
        self.assertIn("Não foi possível conectar", str(cm.exception))
