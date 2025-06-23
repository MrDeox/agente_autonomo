# MANIFESTO DO AGENTE HEPHAESTUS

## Princípios Fundamentais

1. **Autonomia Orientada a Objetivos**: O agente opera de forma autônoma, buscando evoluir seu conhecimento e capacidades para atingir objetivos cada vez mais complexos.
2. **Auto-consistência**: Todo código gerado ou modificado deve ser validado e testado antes de ser aplicado.
3. **Memória Persistente**: O agente mantém um histórico de objetivos concluídos, capacidades adquiridas e lições aprendidas.
4. **Arquitetura Modular**: Componentes devem ser independentes e substituíveis, com interfaces bem definidas.
5. **Transparência Operacional**: Todas as decisões e ações devem ser registradas e justificáveis.

## Arquitetura Inicial

### Componentes Principais

- **Brain**: Coordenação central, tomada de decisões e interface com modelos LLM
- **Memory**: Armazenamento persistente do estado e histórico do agente
- **Tool Executor**: Execução segura de ferramentas e comandos externos
- **Project Scanner**: Análise e compreensão da estrutura do projeto
- **Code Validator**: Validação de sintaxe e consistência de código
- **Patch Applicator**: Aplicação segura de modificações no código

### Fluxo Operacional

1. Recebe um objetivo de alto nível
2. Analisa o estado atual do projeto
3. Planeja as ações necessárias
4. Valida e executa as ações
5. Atualiza sua memória com os resultados
6. Gera feedback e próximo objetivo

## Interfaces Principais

### API Interna (Core)

- `brain.generate_next_objective()`: Gera o próximo objetivo evolutivo
- `brain.generate_capacitation_objective()`: Cria objetivos para novas capacidades
- `memory.add_completed_objective()`: Registra objetivos concluídos
- `tool_executor.run_pytest()`: Executa testes automatizados
- `patch_applicator.apply_patches()`: Aplica modificações no código

### Interfaces Externas

- **OpenRouter API**: Conexão com modelos LLM
- **Git**: Controle de versão
- **Filesystem**: Leitura/escrita de arquivos do projeto

## Roadmap Inicial

1. Implementação do núcleo funcional (Brain + Memory)
2. Integração com ferramentas básicas (Git, pytest)
3. Capacidade de auto-documentação
4. Mecanismos de auto-validação
5. Evolução arquitetural baseada em objetivos

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