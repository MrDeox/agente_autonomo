# Manifesto de Capacidades do Hephaestus

Este documento descreve as capacidades atuais e desejadas do agente Hephaestus, servindo como um guia para o seu desenvolvimento e para a geração de objetivos estratégicos. O foco principal é o **Aprimoramento Auto Recursivo (RSI)**, onde o agente busca ativamente melhorar suas próprias funções e arquitetura.

---

## 1. Capacidades Atuais

### 1.1. Análise e Planejamento
- **Geração de Objetivos (`agent/brain.py`):**
  - Analisa métricas de código estático (complexidade, tamanho do arquivo/função, cobertura de testes).
  - Analisa o manifesto do projeto (`AGENTS.md`).
  - Gera um objetivo de desenvolvimento com base na análise.
  - **Agora considera a análise de performance (`evolution_log.csv`) para otimizar prompts e estratégias.**
- **Análise de Erros (`agent/agents/error_analyzer.py`):**
  - Classifica falhas (ex: erro de sintaxe, falha de teste).
  - Propõe um prompt de correção para o `ArchitectAgent`.
  - **Pode sugerir objetivos de meta-análise para questionar o objetivo ou a estratégia original.**
- **Planejamento de Patches (`agent/agents/architect_agent.py`):**
  - Recebe um objetivo e o manifesto do projeto.
  - Gera um plano de patches em formato JSON para modificar a base de código.
- **Seleção de Estratégia (`agent/agents/maestro_agent.py`):**
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
  - **O `cycle_runner.py` agora interage com um `QueueManager` para processar objetivos de forma assíncrona.**

### 1.3. Memória e Versionamento
- **Memória Persistente (`agent/memory.py`):**
  - Registra o histórico de objetivos bem-sucedidos e falhos.
  - Fornece contexto histórico para as decisões dos agentes.
- **Versionamento com Git (`agent/git_utils.py`):**
  - Inicializa o repositório Git.
  - Realiza commits automáticos após a validação bem-sucedida das alterações.

### 1.4. Infraestrutura (Nova)
- **Servidor FastAPI (`app.py`):**
  - Executa o Hephaestus como um serviço em segundo plano.
  - Expõe endpoints para submissão de objetivos e verificação de status.
  - Gerencia um thread worker para processar objetivos da fila.
- **Gerenciamento de Fila (`agent/queue_manager.py`):**
  - Permite a comunicação assíncrona de objetivos entre o servidor e o worker do agente.
- **Carregamento de Configuração (`agent/config_loader.py`):**
  - Módulo dedicado para carregar a configuração do agente de forma centralizada.

---

## 2. Capacidades Desejadas (Roadmap RSI)

O desenvolvimento futuro deve focar em aprimorar a capacidade do agente de entender e melhorar a si mesmo.

### 2.1. Meta-Cognição e Análise de Performance
- **Análise de Performance do Agente:**
  - **Objetivo:** Desenvolver a capacidade de analisar o próprio log de evolução (`evolution_log.csv`) para identificar gargalos, estratégias ineficazes e padrões de falha.
  - **Status:** Implementado. O `PerformanceAnalysisAgent` agora fornece uma análise detalhada do `evolution_log.csv`, incluindo taxa de sucesso geral, taxa de sucesso por estratégia e tempo médio de ciclo. O `generate_next_objective` utiliza essa análise para informar a geração de objetivos.
- **Análise de Causa Raiz (Meta-Análise):**
  - **Objetivo:** Aprimorar o `ErrorAnalysisAgent` para que, diante de falhas repetidas, ele possa questionar a validade do objetivo ou da estratégia, em vez de apenas tentar corrigir o código.
  - **Status:** Iniciado. O `ErrorAnalysisAgent` agora pode sugerir objetivos de meta-análise, e o `generate_next_objective` em `agent/brain.py` foi aprimorado para detectar e processar esses objetivos, gerando um novo objetivo estratégico para abordar a causa raiz da falha.

### 2.2. Sistemas Avançados de Meta-Inteligência (IMPLEMENTADO ✅)
- **Sistema de Auto-Otimização de Modelos (`agent/model_optimizer.py`):**
  - **Objetivo:** Capturar dados de performance de alta qualidade e criar datasets de fine-tuning para treinar versões melhoradas dos modelos.
  - **Status:** ✅ Implementado. Sistema completo com captura de performance, análise de qualidade multidimensional, geração automática de datasets JSONL, e otimização evolucionária de prompts baseada em dados reais.
  
- **Sistema de Conhecimento Avançado (`agent/advanced_knowledge_system.py`):**
  - **Objetivo:** Busca inteligente multi-fonte com capacidades de aprendizado contínuo e análise semântica.
  - **Status:** ✅ Implementado. Sistema com busca em DuckDuckGo, GitHub, documentação oficial, otimização de queries com IA, ranking inteligente, cache com TTL, e extração de insights acionáveis.
  
- **Analisador de Causa Raiz (`agent/root_cause_analyzer.py`):**
  - **Objetivo:** Análise profunda multi-camada de falhas para identificar causas raiz sistêmicas e gerar recomendações acionáveis.
  - **Status:** ✅ Implementado. Sistema com metodologia "5 Whys", análise em 5 camadas causais, detecção de padrões temporais, análise preditiva, e geração de recomendações específicas.

### 2.3. Aprimoramento da Arquitetura e Estratégia
- **Estratégias de Validação Dinâmicas:**
  - **Objetivo:** Permitir que o `MaestroAgent` não apenas escolha, mas também proponha a criação de novas estratégias de validação com base no contexto da tarefa.
  - **Status:** Avançado. Com o sistema de conhecimento avançado, o agente agora pode pesquisar melhores práticas e implementar estratégias baseadas em conhecimento externo.
  
- **Refatoração Orientada a Capacidades:**
  - **Objetivo:** Garantir que os objetivos de refatoração estejam sempre ligados a um aprimoramento de capacidade, e não apenas à melhoria de métricas de código.
  - **Status:** Avançado. O analisador de causa raiz identifica oportunidades de melhoria sistêmica que direcionam refatorações orientadas a capacidades.

### 2.4. Expansão de Ferramentas (SIGNIFICATIVAMENTE EXPANDIDO ✅)
- **Auto-Aprimoramento de Ferramentas:**
  - **Objetivo:** Dar ao agente a capacidade de modificar e aprimorar suas próprias ferramentas quando uma tarefa falha devido a uma limitação da ferramenta.
  - **Status:** ✅ Parcialmente Implementado. O modelo optimizer identifica padrões de falha e pode gerar datasets para treinar versões melhoradas das ferramentas.

- **Acesso e Raciocínio com Conhecimento Externo:**
  - **Objetivo:** Implementar uma ferramenta de busca na web robusta, permitindo que o agente pesquise documentação de APIs, soluções para erros e novas bibliotecas.
  - **Status:** ✅ Implementado. Sistema completo de busca inteligente multi-fonte com análise semântica e aprendizado contínuo.

- **Gerenciamento de Estratégias Dinâmicas:**
  - **Objetivo:** O `MaestroAgent` deve evoluir de um simples selecionador de estratégias para um arquiteto de estratégias.
  - **Status:** ✅ Avançado. Integração com sistemas de conhecimento permite pesquisa de melhores práticas e implementação de estratégias baseadas em evidências externas.
