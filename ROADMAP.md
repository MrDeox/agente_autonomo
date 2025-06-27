# Hephaestus Agent - Roadmap de Evolução

Este documento delineia os upgrades planejados para o agente Hephaestus, em ordem de prioridade. O objetivo é seguir este roadmap para impulsionar o ciclo de autoaperfeiçoamento recursivo do agente.

## Tier S: Game-Changers (Maior Impacto)

- [] **1. Geração Automática de Testes:**
  -   **Status:** Não iniciado..
  -   **Descrição:** Dar ao agente a capacidade de identificar módulos sem testes e escrever novos arquivos de teste (`test_*.py`) para eles. Isso remove o principal gargalo para refatorações seguras e acelera a robustez do agente.
  -   **Plano:**
      -   [] Modificar `brain.py` para gerar objetivos específicos de criação de testes quando `analyze_code_metrics` encontrar módulos sem cobertura.
      -   [] Aprimorar o prompt do `ArchitectAgent` para que ele possa gerar o conteúdo de um arquivo de teste completamente novo, incluindo imports e funções de teste placeholder.
      -   [] Criar uma nova estratégia de validação em `hephaestus_config.json` para lidar com a criação de novos arquivos de teste e validar sua sintaxe e execução inicial com `pytest`.

- [] **2. Acesso a Conhecimento Externo (Web Search):**
  -   **Status:** Não iniciado..
  -   **Descrição:** Implementar uma nova ferramenta `web_search` que permita ao agente pesquisar na internet para resolver erros ou aprender sobre novas bibliotecas. Isso quebra a "bolha" do agente, permitindo que ele resolva problemas para os quais não foi explicitamente programado.

- [] **3. Consciência da Performance em Runtime:**
  -   **Status:** Não iniciado.
  -   **Descrição:** Fazer com que o agente meça seu próprio tempo de execução e uso de memória. Isso adiciona um novo eixo de otimização (eficiência) e permite que ele detecte e corrija regressões de performance.

## Tier A: Aceleradores Estratégicos

- [ ] **4. Uso Avançado de Git (Feature Branches):**
  -   **Status:** Não iniciado.
  -   **Descrição:** Mudar o fluxo de trabalho para que cada objetivo seja desenvolvido em uma `feature branch` separada. Isso torna o processo mais limpo e seguro, eliminando a necessidade de `git reset --hard` em caso de falha.

- [ ] **5. Análise de Logs em Runtime:**
  -   **Status:** Não iniciado.
  -   **Descrição:** Dar ao agente a capacidade de ler e interpretar seu próprio arquivo de log (`hephaestus.log`) para encontrar e corrigir warnings ou erros não fatais.

## Tier B: Refinamentos e Saúde a Longo Prazo

- [ ] **6. Debate Multi-Agente para Soluções:**
  -   **Status:** Não iniciado.
  -   **Descrição:** Instanciar múltiplos `ArchitectAgent` em paralelo para gerar diferentes soluções para o mesmo problema, com um "CouncilAgent" para decidir a melhor abordagem.

- [ ] **7. Modo de Desenvolvimento Guiado por Testes (TDD):**
  -   **Status:** Não iniciado.
  -   **Descrição:** Implementar uma estratégia onde o agente primeiro escreve um teste que falha e, em seguida, escreve o código para fazê-lo passar.

- [ ] **8. Planejamento Estratégico de Longo Prazo (Roadmap):**
  -   **Status:** Não iniciado.
  -   **Descrição:** Permitir que o agente crie um roadmap de alto nível para si mesmo, em vez de gerar um objetivo de cada vez.

- [ ] **9. Gerenciamento de Dependências:**
  -   **Status:** Não iniciado.
  -   **Descrição:** Fazer com que o agente verifique `requirements.txt` e proponha atualizações para dependências desatualizadas.

## Tier C: Melhorias de Usabilidade e Manutenção

- [ ] **10. Documentação Automática de Código:**
  -   **Status:** Não iniciado.
  -   **Descrição:** Capacitar o agente a gerar ou atualizar automaticamente a documentação de funções, classes e módulos, seguindo padrões como docstrings Python.

- [ ] **11. Refatoração de Código Legado:**
  -   **Status:** Não iniciado.
  -   **Descrição:** Desenvolver a capacidade do agente de identificar e refatorar seções de código consideradas "legado" ou de baixa qualidade, melhorando a manutenibilidade.

- [ ] **12. Otimização de Configurações:**
  -   **Status:** Não iniciado.
  -   **Descrição:** Permitir que o agente analise e proponha otimizações para arquivos de configuração (`hephaestus_config.json`, `example_config.json`), ajustando parâmetros para melhor performance ou robustez.
