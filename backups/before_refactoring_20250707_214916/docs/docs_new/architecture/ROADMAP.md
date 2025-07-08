# Roadmap de Evolução do Hephaestus

Este documento delineia a visão de alto nível para a evolução do Hephaestus como um agente de **Aprimoramento Auto Recursivo (RSI)**. Ele serve como um guia estratégico, enquanto o `CAPABILITIES.md` detalha os passos táticos.

---

## Fase 1: Consciência e Correção (Curto Prazo)

O foco desta fase é fazer com que o agente pare de executar tarefas cegamente e comece a entender seu próprio desempenho e a corrigir suas falhas de forma mais inteligente.

-   [x] **1. Análise de Performance:**
    -   **Visão:** O agente deve ser capaz de ler seu próprio log de performance (`evolution_log.csv`) e responder a perguntas como: "Qual é a minha taxa de sucesso?", "Quais estratégias falham mais?" e "Onde estou gastando mais tempo?".
    -   **Status:** Implementado. O `PerformanceAnalysisAgent` agora fornece uma análise detalhada do `evolution_log.csv`, incluindo taxa de sucesso geral, taxa de sucesso por estratégia e tempo médio de ciclo. O `generate_next_objective` utiliza essa análise para informar a geração de objetivos.

-   [x] **2. Meta-Análise de Falhas:**
    -   **Visão:** Quando uma tarefa falha repetidamente, o agente deve parar de tentar corrigir o código e, em vez disso, questionar o objetivo em si. Ele deve ser capaz de concluir: "Esta abordagem não está funcionando, preciso de uma nova estratégia ou de uma nova ferramenta".
    -   **Status:** Iniciado. O `ErrorAnalysisAgent` agora pode sugerir objetivos de meta-análise, e o `generate_next_objective` em `agent/brain.py` foi aprimorado para detectar e processar esses objetivos, gerando um novo objetivo estratégico para abordar a causa raiz da falha.

-   [ ] **3. Refatoração Orientada a Capacidades:**
    -   **Visão:** O agente só deve propor refatorações de código se elas estiverem diretamente ligadas a um objetivo de capacitação, como "preciso refatorar este módulo para conseguir implementar uma nova ferramenta de análise".
    -   **Status:** Não iniciado. (A base para isso foi estabelecida com a meta-análise e otimização de prompts, mas a refatoração explícita orientada a capacidades ainda não foi implementada).

---

## Fase 2: Expansão de Habilidades (Médio Prazo)

Com a consciência básica estabelecida, o foco se volta para a expansão proativa de suas próprias habilidades e ferramentas.

-   [ ] **1. Auto-Aprimoramento de Ferramentas:**
    -   **Visão:** O agente deve ser capaz de modificar suas próprias ferramentas (`tool_executor.py`, `validation_steps/`, etc.) quando encontrar uma limitação. Se uma validação é muito fraca ou uma ferramenta não tem um parâmetro necessário, ele deve ser capaz de adicioná-lo.
    -   **Status:** Não iniciado. (A meta-análise de falhas pode identificar a necessidade de aprimoramento de ferramentas, mas a implementação autônoma ainda não está presente).

-   [ ] **2. Acesso e Raciocínio com Conhecimento Externo:**
    -   **Visão:** Implementar uma ferramenta de busca na web (`web_search`) robusta, permitindo que o agente pesquise documentação de APIs, soluções para erros e novas bibliotecas para resolver problemas que estão além de seu conhecimento atual.
    -   **Status:** Não iniciado.

-   [x] **3. Gerenciamento de Estratégias Dinâmicas:**
    -   **Visão:** O `MaestroAgent` deve evoluir de um simples selecionador de estratégias para um arquiteto de estratégias. Ele deve ser capaz de propor, e até mesmo codificar, novas estratégias de validação em `hephaestus_config.json` com base nos requisitos de um objetivo.
    -   **Status:** Iniciado. O `generate_next_objective` agora inclui a otimização de prompts e estratégias como uma prioridade, permitindo que o agente proponha modificações em `hephaestus_config.json` ou refinamento de prompts existentes com base na análise de performance.

---

## Fase 3: Autonomia Estratégica (Longo Prazo)

Nesta fase, o agente transcende a execução de ciclos e começa a gerenciar seu próprio desenvolvimento de forma estratégica.

-   [ ] **1. Planejamento de Longo Prazo:**
    -   **Visão:** O agente deve ser capaz de analisar este próprio `ROADMAP.md` e o `CAPABILITIES.md` para gerar um plano de desenvolvimento de múltiplos passos para si mesmo, em vez de operar em um ciclo de objetivo único.
    -   **Status:** Não iniciado.

-   [ ] **2. Auto-Otimização de Modelos:**
    -   **Visão:** Capturar os prompts e as respostas de maior sucesso para criar conjuntos de dados de fine-tuning. O objetivo final é treinar versões especializadas dos modelos de LLM que sejam mais eficientes e precisas para as tarefas do Hephaestus.
    -   **Status:** Não iniciado.

-   [ ] **3. Arquitetura de Agentes Dinâmica:**
    -   **Visão:** O agente deve ser capaz de propor e implementar mudanças em sua própria arquitetura de agentes, como criar um novo agente especializado (ex: `DocumentationAgent`) ou dividir as responsabilidades de um agente existente, para melhorar a eficiência do sistema.
    -   **Status:** Não iniciado.

---

## Arquitetura de Servidor (Novo)

-   [x] **1. Transformação em Servidor FastAPI:**
    -   **Visão:** O Hephaestus opera como um servidor em segundo plano, permitindo a submissão assíncrona de objetivos e monitoramento de status via API.
    -   **Status:** Implementado. O `main.py` agora inicia um servidor FastAPI, e o agente é executado em um thread worker separado, utilizando um `QueueManager` para gerenciar os objetivos.
