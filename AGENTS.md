# Sumário do Código e Interfaces do Projeto Hephaestus

Este documento fornece uma visão geral da estrutura de arquivos e das principais interfaces (APIs internas) do projeto Hephaestus. Ele é gerado e/ou atualizado periodicamente para auxiliar na compreensão do código.

## 1. Estrutura de Arquivos

```
.
├── .coverage
├── .gitignore
├── AGENTS.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── HEPHAESTUS_MEMORY.json
├── ISSUES.md
├── MANIFESTO.md
├── README.md
├── ROADMAP.md
├── agent/
│   ├── __init__.py
│   ├── agents.py
│   ├── brain.py
│   ├── code_validator.py
│   ├── cycle_runner.py
│   ├── deep_validator.py
│   ├── error_analyzer.py
│   ├── git_utils.py
│   ├── memory.py
│   ├── patch_applicator.py
│   ├── project_scanner.py
│   ├── state.py
│   ├── tool_executor.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── llm_client.py
│   └── validation_steps/
│       ├── __init__.py
│       ├── base.py
│       ├── patch_applicator.py
│       ├── pytest_new_file_validator.py
│       ├── pytest_validator.py
│       ├── self_improvement_validator.py
│       └── syntax_validator.py
├── example_config.json
├── hephaestus.log
├── hephaestus_config.json
├── main.py
├── requirements.txt
└── tests/
    ├── __init__.py
    ├── agent/
    │   ├── __init__.py
    │   ├── test_brain.py
    │   ├── test_error_analyzer.py
    │   ├── test_patch_applicator.py
    │   ├── test_tool_executor.py
    │   ├── test_web_search.py
    │   ├── utils/
    │   │   ├── __init__.py
    │   │   └── test_llm_client.py
    │   └── validation_steps/
    │       ├── __init__.py
    │       ├── test_pytest_new_file_validator.py
    │       └── test_self_improvement_validator.py
    ├── conftest.py
    ├── test_agents.py
    ├── test_brain.py
    ├── test_code_validator.py
    ├── test_config_loading.py
    ├── test_deep_validator.py
    ├── test_hephaestus.py
    ├── test_memory.py
    ├── test_patch_applicator.py
    └── test_project_scanner.py
```

*Nota: Esta estrutura é uma representação simplificada e pode não incluir todos os arquivos e diretórios.*

## 2. Resumo das Interfaces (APIs Internas)

### Arquivo: `main.py`
- **Classe:** `HephaestusAgent`
  - *Classe principal que encapsula a lógica do agente autônomo.*

### Arquivo: `agent/deep_validator.py`
- **Função:** `analyze_complexity(code_string: str)`
  - *Analisa a complexidade ciclomática e outras métricas da string de código Python fornecida usando Radon.*
- **Função:** `calculate_quality_score(complexity_report: dict, duplication_report: list)`
  - *Calcula uma pontuação de qualidade com base na complexidade, duplicação e outras métricas de código.*
- **Função:** `_get_code_lines(code_string: str, strip_comments_blanks: bool=True)`
  - *Retorna uma lista de tuplas (número_linha_original, conteudo_linha).*
- **Função:** `_find_duplicates_for_block(block_to_check: list[str], all_lines: list[tuple[int, str]], start_index: int, min_lines: int)`
  - *Encontra ocorrências de `block_to_check` em `all_lines`, começando após `start_index`.*
- **Função:** `detect_code_duplication(code_string: str, min_lines: int=4, strip_comments_and_blanks: bool=True)`
  - *Detecta blocos de código duplicados na string de código Python fornecida.*

### Arquivo: `agent/brain.py`
- **Função:** `generate_next_objective(api_key: str, model: str, current_manifest: str, logger: logging.Logger, project_root_dir: str, config: Optional[Dict[str, Any]]=None, base_url: str='https://openrouter.ai/api/v1', memory_summary: Optional[str]=None)`
  - *Gera o próximo objetivo evolutivo usando um modelo leve e análise de código.*
- **Função:** `generate_capacitation_objective(api_key: str, model: str, engineer_analysis: str, base_url: str='https://openrouter.ai/api/v1', memory_summary: Optional[str]=None, logger: Optional[logging.Logger]=None)`
  - *Gera um objetivo para criar novas capacidades necessárias.*
- **Função:** `generate_commit_message(api_key: str, model: str, analysis_summary: str, objective: str, logger: logging.Logger, base_url: str='https://openrouter.ai/api/v1')`
  - *Gera uma mensagem de commit concisa e informativa usando um LLM.*

### Arquivo: `agent/__init__.py`
  - *Arquivo de inicialização do pacote `agent`.*

### Arquivo: `agent/git_utils.py`
- **Função:** `initialize_git_repository(logger: logging.Logger)`
  - *Garante que um repositório git exista e esteja configurado.*

### Arquivo: `agent/code_validator.py`
- **Função:** `perform_deep_validation(file_path: Path, logger: logging.Logger)`
  - *Realiza uma análise profunda da qualidade do código Python.*
- **Função:** `validate_python_code(file_path: str | Path, logger: logging.Logger, perform_deep_analysis: bool=True)`
  - *Valida se o código Python em um arquivo é sintaticamente correto e, opcionalmente, realiza uma análise profunda.*
- **Função:** `validate_json_syntax(file_path: str | Path, logger: logging.Logger)`
  - *Valida se um arquivo contém JSON válido.*

### Arquivo: `agent/agents.py`
- **Função:** `parse_json_response(raw_str: str, logger: logging.Logger)`
  - *Analisa uma string bruta que se espera conter JSON, limpando-a e decodificando-a.*
- **Classe:** `ArchitectAgent`
  - *Agente responsável por gerar código e patches com base em um objetivo.*
- **Classe:** `MaestroAgent`
  - *Agente orquestrador que pode interagir com outros agentes ou ferramentas.*

### Arquivo: `agent/patch_applicator.py`
- **Função:** `_handle_insert(full_path: Path, lines: list[str], instruction: dict, logger: logging.Logger)`
  - *Aplica um patch do tipo INSERT e retorna `(sucesso, linhas_atualizadas)`.*
- **Função:** `_handle_replace(full_path: Path, lines: list[str], instruction: dict, logger: logging.Logger)`
  - *Aplica um patch do tipo REPLACE.*
- **Função:** `_handle_delete_block(full_path: Path, lines: list[str], instruction: dict, logger: logging.Logger)`
  - *Aplica um patch do tipo DELETE_BLOCK.*
- **Função:** `apply_patches(instructions: list[dict], logger: logging.Logger, base_path: str='.')`
  - *Aplica uma lista de instruções de patch aos arquivos.*

### Arquivo: `agent/cycle_runner.py`
- **Função:** `run_cycles(agent: 'HephaestusAgent')`
  - *Executa o loop principal de evolução para o agente fornecido.*

### Arquivo: `agent/memory.py`
- **Classe:** `Memory`
  - *Gerencia a memória persistente para o agente Hephaestus, armazenando dados históricos.*

### Arquivo: `agent/tool_executor.py`
- **Função:** `run_pytest(test_dir: str='tests/', cwd: str | Path | None=None)`
  - *Executa testes pytest no diretório especificado e retorna os resultados.*
- **Função:** `check_file_existence(file_paths: list[str])`
  - *Verifica se todos os arquivos especificados existem.*
- **Função:** `run_in_sandbox(temp_dir_path: str, objective: str)`
  - *Executa o `main.py` de um diretório isolado, monitorando tempo e memória.*
- **Função:** `run_git_command(command: list[str])`
  - *Executa um comando Git e retorna o status e a saída.*
- **Função:** `web_search(query: str)`
  - *Realiza uma pesquisa na web usando a API DuckDuckGo e retorna os resultados.*

### Arquivo: `agent/project_scanner.py`
- **Função:** `_extract_elements(code_string: str)`
  - *Extrai elementos (classes, funções) de uma string de código.*
- **Função:** `_extract_skeleton(code_string: str)`
  - *Extrai o esqueleto (definições sem corpo) de uma string de código.*
- **Função:** `update_project_manifest(root_dir: str, target_files: List[str], output_path: str='AGENTS.MD', excluded_dir_patterns: Optional[List[str]]=None)`
  - *Atualiza o manifesto do projeto (este arquivo) com base nos arquivos alvo.*
- **Função:** `analyze_code_metrics(root_dir: str, excluded_dir_patterns: Optional[List[str]]=None, file_loc_threshold: int=300, func_loc_threshold: int=50, func_cc_threshold: int=10)`
  - *Analisa arquivos Python em um diretório para métricas de código como LOC e Complexidade Ciclomática.*

### Arquivo: `agent/state.py`
- **Classe:** `AgentState`
  - *Representa o estado interno do agente Hephaestus durante um ciclo de processamento.*

### Arquivo: `agent/error_analyzer.py`
- **Classe:** `ErrorAnalysisAgent`
  - *Analisa falhas ocorridas durante a execução de um objetivo, classifica o erro e sugere ações corretivas.*
  - **Método:** `analyze_error(failed_objective: str, error_reason: str, error_context: str, original_patches: Optional[str]=None, failed_code_snippet: Optional[str]=None, test_output: Optional[str]=None) -> Dict[str, Any]`
    - *Recebe detalhes da falha e retorna um dicionário com a classificação do erro, tipo de sugestão (ex: REGENERATE_PATCHES, NEW_OBJECTIVE) e um prompt sugerido para a próxima ação.*

### Arquivo: `hephaestus_config.json` (Estrutura e Estratégias Notáveis)
- *Arquivo de configuração principal para o Hephaestus.*
- **Seção:** `validation_strategies`
  - *Define várias estratégias de validação e aplicação de patches. Cada estratégia é uma sequência de etapas (steps).*
  - **Estratégia Notável:** `AUTO_CORRECTION_STRATEGY`
    - *Usada programaticamente pelo `CycleRunner` quando um objetivo de correção automática está sendo processado.*
    - *Tipicamente envolve etapas como `validate_syntax`, `apply_patches_to_disk`, e `run_pytest_validation` para verificar a correção.*

### Arquivo: `agent/validation_steps/pytest_validator.py`
- **Classe:** `PytestValidator(ValidationStep)`
  - *Executa pytest como uma etapa de validação.*

### Arquivo: `agent/validation_steps/self_improvement_validator.py`
- **Classe:** `SelfImprovementValidator`
  - *Validador para o processo de autoaperfeiçoamento, possivelmente verificando se as metas de melhoria foram alcançadas.*

### Arquivo: `agent/validation_steps/__init__.py`
- **Função:** `get_validation_step(name: str)`
  - *Retorna uma instância da etapa de validação com base no nome fornecido.*

### Arquivo: `agent/validation_steps/base.py`
- **Classe:** `ValidationStep(ABC)`
  - *Classe base abstrata para uma etapa de validação.*

### Arquivo: `agent/validation_steps/patch_applicator.py`
- **Classe:** `PatchApplicatorStep(ValidationStep)`
  - *Aplica patches ao caminho base especificado como uma etapa de validação.*

### Arquivo: `agent/validation_steps/syntax_validator.py`
- **Classe:** `SyntaxValidator(ValidationStep)`
  - *Valida a sintaxe de arquivos Python e JSON.*

### Arquivo: `agent/validation_steps/pytest_new_file_validator.py`
- **Classe:** `PytestNewFileValidator(ValidationStep)`
  - *Uma etapa de validação que executa pytest especificamente em arquivos de teste recém-criados.*

### Arquivo: `agent/utils/__init__.py`
  - *Arquivo de inicialização do pacote `utils`.*

### Arquivo: `agent/utils/llm_client.py`
- **Função:** `call_llm_api(api_key: str, model: str, prompt: str, temperature: float, base_url: str, logger: logging.Logger)`
  - *Função auxiliar para fazer chamadas à API do LLM.*

*Nota: A seção "CONTEÚDO COMPLETO DOS ARQUIVOS ALVO" foi removida por estar vazia e para manter este documento focado no resumo das interfaces e estrutura.*
