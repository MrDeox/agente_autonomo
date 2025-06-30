# Manifesto de Capacidades do Hephaestus

Este documento descreve as capacidades atuais e desejadas do agente Hephaestus, servindo como um guia para o seu desenvolvimento e para a geração de objetivos estratégicos. O foco principal é o **Aprimoramento Auto Recursivo (RSI)**, onde o agente busca ativamente melhorar suas próprias funções e arquitetura.

---

## 1. Capacidades Atuais

### 1.1. Análise e Planejamento
- **Geração de Objetivos (`agent/brain.py`):**
  - Analisa métricas de código estático (complexidade, tamanho do arquivo/função, cobertura de testes).
  - Analisa o manifesto do projeto (`AGENTS.md`).
  - Gera um objetivo de desenvolvimento com base na análise.
- **Análise de Erros (`agent/error_analyzer.py`):**
  - Classifica falhas (ex: erro de sintaxe, falha de teste).
  - Propõe um prompt de correção para o `ArchitectAgent`.
- **Planejamento de Patches (`agent/agents.py:ArchitectAgent`):**
  - Recebe um objetivo e o manifesto do projeto.
  - Gera um plano de patches em formato JSON para modificar a base de código.
- **Seleção de Estratégia (`agent/agents.py:MaestroAgent`):**
  - Analisa o plano de patches.
  - Escolhe uma estratégia de validação apropriada (ex: apenas sintaxe, sintaxe e testes).

### 1.2. Execução e Validação
- **Aplicação de Patches (`agent/patch_applicator.py`):**
  - Aplica as modificações de código propostas em um ambiente de sandbox.
- **Validação de Sintaxe (`agent/validation_steps/syntax_validator.py`):**
  - Verifica a sintaxe de arquivos Python e JSON.
- **Execução de Testes (`agent/validation_steps/pytest_validator.py`):**
  - Executa a suíte de testes `pytest` para validar as alterações.
- **Gerenciamento de Estado e Ciclo (`agent/state.py`, `agent/cycle_runner.py`):**
  - Orquestra o fluxo completo de um ciclo de evolução.
  - Mantém o estado do ciclo atual (objetivo, patches, resultado da validação).

### 1.3. Memória e Versionamento
- **Memória Persistente (`agent/memory.py`):**
  - Registra o histórico de objetivos bem-sucedidos e falhos.
  - Fornece contexto histórico para as decisões dos agentes.
- **Versionamento com Git (`agent/git_utils.py`):**
  - Inicializa o repositório Git.
  - Realiza commits automáticos após a validação bem-sucedida das alterações.

---

## 2. Capacidades Desejadas (Roadmap RSI)

O desenvolvimento futuro deve focar em aprimorar a capacidade do agente de entender e melhorar a si mesmo.

### 2.1. Meta-Cognição e Análise de Performance
- **Análise de Performance do Agente:**
  - **Objetivo:** Desenvolver a capacidade de analisar o próprio log de evolução (`evolution_log.csv`) para identificar gargalos, estratégias ineficazes e padrões de falha.
  - **Próximo Passo:** Criar um novo agente, `PerformanceAnalysisAgent`, que lê o log e gera um resumo de performance.
- **Análise de Causa Raiz (Meta-Análise):**
  - **Objetivo:** Aprimorar o `ErrorAnalysisAgent` para que, diante de falhas repetidas, ele possa questionar a validade do objetivo ou da estratégia, em vez de apenas tentar corrigir o código.
  - **Próximo Passo:** Modificar o prompt do `ErrorAnalysisAgent` para incluir perguntas de meta-análise e a capacidade de gerar um `[META-ANALYSIS]` como objetivo.

### 2.2. Aprimoramento da Arquitetura e Estratégia
- **Estratégias de Validação Dinâmicas:**
  - **Objetivo:** Permitir que o `MaestroAgent` não apenas escolha, mas também proponha a criação de novas estratégias de validação com base no contexto da tarefa.
  - **Próximo Passo:** Implementar um fluxo onde o `MaestroAgent` pode retornar `NEW_STRATEGY_REQUIRED`, acionando um objetivo de capacitação para criar uma nova entrada em `hephaestus_config.json`.
- **Refatoração Orientada a Capacidades:**
  - **Objetivo:** Garantir que os objetivos de refatoração estejam sempre ligados a um aprimoramento de capacidade, e não apenas à melhoria de métricas de código.
  - **Próximo Passo:** Refinar o prompt do `generate_next_objective` para exigir uma justificativa de capacitação para qualquer refatoração proposta.

### 2.3. Expansão de Ferramentas
- **Auto-Aprimoramento de Ferramentas:**
  - **Objetivo:** Dar ao agente a capacidade de modificar e aprimorar suas próprias ferramentas (ex: `tool_executor.py`) quando uma tarefa falha devido a uma limitação da ferramenta.
  - **Próximo Passo:** Criar um fluxo de "capacitação de ferramenta" que é acionado quando uma falha é classificada como `TOOL_ERROR`.
