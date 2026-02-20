import yaml
from typing import Any, Dict, List
from kubernetes import client, config, utils
from kubernetes.client.rest import ApiException
from django.core.exceptions import ValidationError

def get_kubernetes_client():
    """
    Tenta carregar a configuração do Kubernetes.
    Em dev, usa o kubeconfig local. Em prod, usa in-cluster config.
    """
    try:
        config.load_kube_config()
    except config.ConfigException:
        try:
            config.load_incluster_config()
        except config.ConfigException:
            # Para testes locais onde não há cluster, retornamos None
            # mas em execução real isso deve falhar.
            return None
    return client.ApiClient()

def task_execute_eks(*, yaml_manifest: str, namespace: str = "default") -> List[Dict[str, Any]]:
    """
    Aplica um manifest YAML no cluster Kubernetes.
    Retorna uma lista de resultados para cada recurso processado.
    """
    k8s_client = get_kubernetes_client()
    if not k8s_client:
        raise ValidationError("Não foi possível conectar ao cluster Kubernetes.")

    try:
        # Carrega múltiplos documentos YAML se presentes
        docs = list(yaml.safe_load_all(yaml_manifest))
    except yaml.YAMLError as e:
        raise ValidationError(f"Erro ao processar YAML: {str(e)}")

    results = []
    
    # Criamos um arquivo temporário ou passamos os docs diretamente se o utils suportar
    # O utils.create_from_dict é mais seguro para processar via API.
    for doc in docs:
        if not doc:
            continue
            
        try:
            utils.create_from_dict(k8s_client, doc, namespace=namespace)
            results.append({
                "kind": doc.get("kind"),
                "name": doc.get("metadata", {}).get("name"),
                "status": "CREATED"
            })
        except ApiException as e:
            # Se já existir, tentamos tratar como UPDATE (opcional dependendo da regra)
            if e.status == 409: # Conflict (Already Exists)
                results.append({
                    "kind": doc.get("kind"),
                    "name": doc.get("metadata", {}).get("name"),
                    "status": "ALREADY_EXISTS",
                    "detail": "O recurso já existe no cluster."
                })
            else:
                results.append({
                    "kind": doc.get("kind"),
                    "name": doc.get("metadata", {}).get("name"),
                    "status": "FAILED",
                    "error": str(e)
                })
        except Exception as e:
            results.append({
                "kind": doc.get("kind"),
                "name": doc.get("metadata", {}).get("name"),
                "status": "ERROR",
                "error": str(e)
            })

    return results
