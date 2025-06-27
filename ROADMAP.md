# Hephaestus Agent - Roadmap de Evolução

Este documento delineia os upgrades planejados para o agente Hephaestus, em ordem de prioridade. O objetivo é seguir este roadmap para impulsionar o ciclo de autoaperfeiçoamento recursivo do agente.

## Tier S: Game-Changers (Maior Impacto)

- [x] **1. Geração Automática de Testes:**
  -   **Status:** Concluído.
  -   **Descrição:** Dar ao agente a capacidade de identificar módulos sem testes e escrever novos arquivos de teste (`test_*.py`) para eles. Isso remove o principal gargalo para refatorações seguras e acelera a robustez do agente.
  -   **Implementação:**
      -   [x] `agent/project_scanner.py` (`analyze_code_metrics`) já identificava módulos sem testes (`missing_tests`).
      -   [x] `agent/brain.py` (`generate_next_objective`) teve seu prompt atualizado para melhor instruir o LLM a gerar objetivos de criação de testes, especificando o nome do novo arquivo de teste.
      -   [x] `agent/agents.py` (`ArchitectAgent`) teve seu prompt atualizado para, ao receber um objetivo de criação de testes, gerar o conteúdo completo do novo arquivo de teste, incluindo imports e funções de teste placeholder.
      -   [x] Criada a estratégia de validação `CREATE_NEW_TEST_FILE_STRATEGY` em `hephaestus_config.json`.
      -   [x] Criado o validador `PytestNewFileValidator` (em `agent/validation_steps/pytest_new_file_validator.py`) que executa `pytest` especificamente no novo arquivo de teste gerado.
      -   [x] Adicionados testes unitários para `PytestNewFileValidator`.

- [] **2. Acesso a Conhecimento Externo (Web Search):**
  -   **Status:** Não iniciado.
  -   **Descrição:** Implementar uma nova ferramenta `web_search` que permita ao agente pesquisar na internet para resolver erros ou aprender sobre novas bibliotecas. Isso quebra a "bolha" do agente, permitindo que ele resolva problemas para os quais não foi explicitamente programado.

- [] **3. Consciência da Performance em Runtime:**
  -   **Status:** Não iniciado.
  -   **Descrição:** Fazer com que o agente meça seu próprio tempo de execução e uso de memória. Isso adiciona um novo eixo de otimização (eficiência) e permite que ele detecte e corrija regressões de performance.

- [ ] **4. Memória de Longo Prazo (Banco Vetorial):**  
  -   **Status:** Não iniciado.
  -   **Descrição:** Adotar banco de vetores (ex: Pinecone) para armazenar embeddings de objetivos e resultados, permitindo buscas semânticas eficientes e enriquecendo o contexto dos prompts.

- [ ] **5. Aprendizado Reforçado:**  
  -   **Status:** Não iniciado.
  -   **Descrição:** Integrar RL para aprimorar escolha de estratégias, recompensando objetivos alcançados e penalizando falhas (híbrido LLM+RL).

- [ ] **6. Auto-treino do Modelo:**  
  -   **Status:** Não iniciado.
  -   **Descrição:** Capturar dados de ciclos para treinar modelo interno otimizado, reduzindo dependência de APIs externas.

## Tier A: Aceleradores Estratégicos

- [ ] **1. Uso Avançado de Git (Feature Branches):**
  -   **Status:** Não iniciado.
  -   **Descrição:** Mudar o fluxo de trabalho para que cada objetivo seja desenvolvido em uma `feature branch` separada. Isso torna o processo mais limpo e seguro, eliminando a necessidade de `git reset --hard` em caso de falha.

- [ ] **2. Análise de Logs em Runtime:**
  -   **Status:** Não iniciado.
  -   **Descrição:** Dar ao agente a capacidade de ler e interpretar seu próprio arquivo de log (`hephaestus.log`) para encontrar e corrigir warnings ou erros não fatais.

- [ ] **3. Modularização e PLUGINS:**  
  -   **Status:** Não iniciado.
  -   **Descrição:** Extrair funcionalidades em serviços desacoplados (microservices/plugins) para facilitar testes e escalonamento.

- [ ] **4. Cobertura de Testes e CI:**  
  -   **Status:** Não iniciado.
  -   **Descrição:** Implementar suíte de testes abrangente e pipeline CI/CD para garantir estabilidade.

## Tier B: Refinamentos e Saúde a Longo Prazo

- [ ] **1. Debate Multi-Agente para Soluções:**
  -   **Status:** Não iniciado.
  -   **Descrição:** Instanciar múltiplos `ArchitectAgent` em paralelo para gerar diferentes soluções para o mesmo problema, com um "CouncilAgent" para decidir a melhor abordagem.

- [ ] **2. Modo de Desenvolvimento Guiado por Testes (TDD):**
  -   **Status:** Não iniciado.
  -   **Descrição:** Implementar uma estratégia onde o agente primeiro escreve um teste que falha e, em seguida, escreve o código para fazê-lo passar.

- [ ] **3. Planejamento Estratégico de Longo Prazo (Roadmap):**
  -   **Status:** Não iniciado.
  -   **Descrição:** Permitir que o agente crie um roadmap de alto nível para si mesmo, em vez de gerar um objetivo de cada vez.

- [ ] **4. Gerenciamento de Dependências:**
  -   **Status:** Não iniciado.
  -   **Descrição:** Fazer com que o agente verifique `requirements.txt` e proponha atualizações para dependências desatualizadas.

- [ ] **5. Expansão Multi-Agente:**  
  -   **Status:** Não iniciado.
  -   **Descrição:** Criar múltiplos agentes especialistas trabalhando em paralelo para acelerar desenvolvimento.

## Tier C: Melhorias de Usabilidade e Manutenção

- [ ] **1. Documentação Automática de Código:**
  -   **Status:** Não iniciado.
  -   **Descrição:** Capacitar o agente a gerar ou atualizar automaticamente a documentação de funções, classes e módulos, seguindo padrões como docstrings Python.

- [ ] **2. Refatoração de Código Legado:**
  -   **Status:** Não iniciado.
  -   **Descrição:** Desenvolver a capacidade do agente de identificar e refatorar seções de código consideradas "legado" ou de baixa qualidade, melhorando a manutenibilidade.

- [ ] **3. Otimização de Configurações:**
  -   **Status:** Não iniciado.
  -   **Descrição:** Permitir que o agente analise e proponha otimizações para arquivos de configuração (`hephaestus_config.json`, `example_config.json`), ajustando parâmetros para melhor performance ou robustez.

- [ ] **4. Interface de Monitoramento:**  
  -   **Status:** Não iniciado.
  -   **Descrição:** Desenvolver dashboard/API para exibir estado do agente em tempo real, facilitando supervisão.
