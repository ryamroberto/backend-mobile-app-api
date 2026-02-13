# Story 2.4: Integração EKS para Automation Tasks (Kubernetes Orchestration)

**Status**: Ready for Review

## Story
**As a** Engenheiro de DevOps/IA,
**I want** aplicar manifests Kubernetes (YAML) via AutomationTasks,
**so that** eu possa automatizar o provisionamento de infraestrutura de suporte a IA no EKS.

## Acceptance Criteria
1. [x] Adicionar `EKS` às opções de `TaskType` no modelo `AutomationTask`.
2. [x] Implementar o service `task_execute_eks` que receba um manifest YAML e o aplique no cluster configurado.
3. [x] Integrar a biblioteca `kubernetes` (Python client) ao projeto.
4. [x] O campo `input_params` da tarefa deve aceitar a chave `yaml_manifest` e `namespace`.
5. [x] O campo `output_results` deve armazenar o retorno do comando `apply` (status do recurso criado/atualizado).
6. [x] REGRA OBRIGATORIO: qualquer texto exibido ao usuario deve estar em portugues (pt-br) se houver ingles, considere um erro.

## 🤖 CodeRabbit Integration
> **CodeRabbit Integration**: Disabled

### Story Type Analysis
**Primary Type**: Infrastructure
**Secondary Type(s)**: API, Cloud
**Complexity**: High

### Specialized Agent Assignment
**Primary Agents**:
- @dev
- @devops

**Supporting Agents**:
- @qa

## Tasks / Subtasks
- [x] **Configuração de Ambiente**
    - [x] Adicionar `kubernetes` ao `requirements.txt`.
    - [x] Configurar autenticação local/EKS (Kubeconfig via env ou IRSA).
- [x] **Evolução do Modelo**
    - [x] Adicionar `EKS` ao `AutomationTask.TaskType`.
- [x] **Implementação do Service**
    - [x] Criar logic em `appdata/services/eks_services.py` para processar manifests YAML.
    - [x] Garantir tratamento de erros para YAMLs inválidos ou falhas de conexão com o cluster.
- [x] **Integração com AutomationTask**
    - [x] Atualizar o flow de execução para permitir o trigger de tarefas EKS.
- [x] **Verificação**
    - [x] Criar testes unitários simulando (mocking) a API do Kubernetes.

## Dev Notes
- Utilizada a biblioteca oficial `kubernetes` para Python.
- O serviço `task_execute_eks` suporta múltiplos documentos YAML em uma única tarefa.
- Fluxo de execução disparado automaticamente quando `execution_status` muda para `RUNNING`.

### Testing
- Executados 21 testes (suíte completa). Todos passaram.
- Testes específicos para `eks_services` cobrem casos de sucesso, falha de conexão e YAML inválido.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 13/02/2026 | 1.0 | Implementação da integração com EKS/Kubernetes | Dex (Dev) |

## QA Results
### QA Decision: PASS ✅

**Validação de Critérios de Aceite:**
1. [x] Orquestração de Kubernetes (EKS) integrada ao modelo `AutomationTask`.
2. [x] Serviço `eks_services.py` funcional para aplicação de manifests YAML.
3. [x] Gestão de estado de execução robusta: transições automáticas baseadas no retorno do cluster.
4. [x] Tratamento de erros e conflitos implementado (ex: identificação de recursos já existentes).
5. [x] Conformidade total com a regra de idioma `pt-br`.

**Análise Técnica:**
- Uso correto da biblioteca oficial do Kubernetes.
- Suíte de testes unitários (21 testes) garante a integridade da integração.
- Migrações de banco de dados consistentes.

— Quinn, guardião da qualidade 🛡️
