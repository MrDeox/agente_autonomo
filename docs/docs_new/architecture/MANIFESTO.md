# MANIFESTO DO AGENTE HEPHAESTUS

## Princípios Fundamentais

1. **Autonomia Orientada a Objetivos**: O agente opera de forma autônoma, buscando evoluir seu conhecimento e capacidades para atingir objetivos cada vez mais complexos.
2. **Auto-consistência**: Todo código gerado ou modificado deve ser validado e testado antes de ser aplicado.
3. **Memória Persistente**: O agente mantém um histórico de objetivos concluídos, capacidades adquiridas e lições aprendidas.
4. **Arquitetura Modular**: Componentes devem ser independentes e substituíveis, com interfaces bem definidas.
5. **Transparência Operacional**: Todas as decisões e ações devem ser registradas e justificáveis.

## Arquitetura e Estado Atual

### Visão Geral da Implementação Atual
O núcleo do sistema Hephaestus reside no diretório `agent/`. É lá que a lógica para o ciclo de operação, a tomada de decisão ("cérebro" ou `brain.py`), e a aplicação de modificações no código (`patch_applicator.py`) estão implementadas. Um componente chave que demonstra a intenção de criar um sistema de autoaperfeiçoamento é o `self_improvement_validator.py`.

O projeto já possui uma base sólida com:
*   Um ciclo de execução principal (`cycle_runner.py`), agora operando em um thread worker separado.
*   Um cérebro centralizado para o agente (`brain.py`), aprimorado para meta-análise e otimização de prompts.
*   Mecanismos para aplicar patches de código (`patch_applicator.py`).
*   Um sistema de validação de sintaxe e testes (`SyntaxValidator`, `PytestValidator`).
*   A capacidade de se autoavaliar e propor melhorias, implementada através do `ErrorAnalysisAgent` (que agora pode sugerir objetivos de meta-análise) e dos mecanismos de geração de objetivos.
*   **Um servidor FastAPI (`app.py`) para submissão assíncrona de objetivos e monitoramento de status.**
*   **Um gerenciador de fila (`queue_manager.py`) para comunicação assíncrona de objetivos.**
*   **Um módulo de carregamento de configuração (`config_loader.py`) para centralizar o gerenciamento de configurações.**

### Componentes Principais (Arquitetura Conceitual)

- **HephaestusAgent**: A classe principal do agente, agora em `agent/hephaestus_agent.py`.
- **Brain**: Coordenação central, tomada de decisões e interface com modelos LLM. Aprimorado para meta-análise e otimização de prompts.
- **Memory**: Armazenamento persistente do estado e histórico do agente.
- **Tool Executor**: Execução segura de ferramentas e comandos externos.
- **Project Scanner**: Análise e compreensão da estrutura do projeto.
- **Code Validator**: Validação de sintaxe e consistência de código.
- **Patch Applicator**: Aplicação segura de modificações no código.
- **Queue Manager**: Gerencia a fila de objetivos para processamento assíncrono.
- **Config Loader**: Carrega e gerencia as configurações do agente.

### Fluxo Operacional (Atualizado)

1.  **Servidor FastAPI (`app.py`)** recebe objetivos via API e os adiciona a uma fila.
2.  Um **thread worker** executa o ciclo principal do agente (`cycle_runner.py`).
3.  O `cycle_runner` obtém um objetivo da fila.
4.  O **Brain** (com o 'Planejador Estratégico Avançado') analisa o estado atual do projeto, métricas de código, histórico de performance e, se for um objetivo de meta-análise, o objetivo original e a razão da falha.
5.  O **ArchitectAgent** planeja as ações necessárias (patches).
6.  O **MaestroAgent** valida e executa as ações, escolhendo a estratégia de validação apropriada (que pode ser influenciada pela otimização de prompts).
7.  O agente atualiza sua **Memory** com os resultados.
8.  O **ErrorAnalysisAgent** analisa falhas e, se necessário, gera um novo objetivo de correção ou um objetivo de meta-análise, que é adicionado de volta à fila.
9.  O ciclo se repete, puxando o próximo objetivo da fila.

## Interfaces Principais

### API Interna (Core)

- `hephaestus_agent.HephaestusAgent`: A classe principal do agente.
- `brain.generate_next_objective()`: Gera o próximo objetivo evolutivo, agora com meta-análise e otimização de prompts.
- `brain.generate_capacitation_objective()`: Cria objetivos para novas capacidades.
- `memory.add_completed_objective()`: Registra objetivos concluídos.
- `tool_executor.run_pytest()`: Executa testes automatizados.
- `patch_applicator.apply_patches()`: Aplica modificações no código.
- `queue_manager.put_objective()`: Adiciona um objetivo à fila.
- `queue_manager.get_objective()`: Obtém um objetivo da fila.
- `config_loader.load_config()`: Carrega a configuração do agente.

### Interfaces Externas

- **FastAPI API**: Para submissão de objetivos e status (HTTP).
- **OpenRouter API**: Conexão com modelos LLM.
- **Git**: Controle de versão.
- **Filesystem**: Leitura/escrita de arquivos do projeto.

## Roadmap Inicial (Histórico)

Esta seção descreve o roadmap inicial que guiou as primeiras fases do projeto. Para o roadmap atual e futuro, consulte o arquivo `ROADMAP.md`.

1. Implementação do núcleo funcional (Brain + Memory)
2. Integração com ferramentas básicas (Git, pytest)
3. Capacidade de auto-documentação (parcialmente alcançada com `AGENTS.md`)
4. Mecanismos de auto-validação (base implementada)
5. Evolução arquitetural baseada em objetivos (em andamento)

## Convenções

- Todos os patches devem ser validados sintaticamente
- Mensagens de commit devem seguir Conventional Commits
- Novas capacidades requerem testes automatizados
- O estado do agente deve ser persistido após cada ciclo

## Visão de Futuro

- Auto-otimização de código
- Geração de documentação automatizada
- Resolução autônoma de issues
- Capacidade de trabalhar em múltiplos projetos