import logging
from typing import Optional, Any
import json
import requests
from datetime import datetime
import json
import logging # Adicionado
import requests # Removido, pois _call_llm_api foi movido para agents.py
import traceback # Removido, pois não é mais usado diretamente aqui
from typing import Optional, Dict, Any, List, Tuple

# As funções parse_json_response e _call_llm_api foram movidas para agent/agents.py
# A função get_action_plan foi movida para ArchitectAgent.plan_action em agent/agents.py
# A função get_maestro_decision foi movida para MaestroAgent.choose_strategy em agent/agents.py

# Funções que permanecem em brain.py:
# - generate_next_objective
# - generate_capacitation_objective
# - generate_commit_message (se não for movida para um agente específico no futuro)

# É necessário manter _call_llm_api aqui se as funções restantes o utilizarem diretamente.
# Vamos verificar se generate_next_objective, generate_capacitation_objective
# e generate_commit_message usam _call_llm_api.
# Sim, elas usam. Então _call_llm_api (e por extensão, requests) precisa ficar ou ser importado.

# _call_llm_api foi movida para agents.py, mas ainda é usada aqui.
# Para evitar dependência circular ou refatoração maior no momento,
# esta função será mantida aqui como uma cópia temporária.
# TODO: Refatorar _call_llm_api para um local compartilhado (ex: utils.llm_client).

from agent.project_scanner import analyze_code_metrics # Nova importação

def _call_llm_api(api_key: str, model: str, prompt: str, temperature: float, base_url: str, logger: Any) -> Tuple[Optional[str], Optional[str]]:
    """Função auxiliar para fazer chamadas à API LLM."""
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        if logger: logger.debug(f"API Response (brain._call_llm_api): {response_json}")
        if "choices" not in response_json:
            return None, f"API response missing 'choices' key. Full response: {response_json}"
        content = response_json["choices"][0]["message"]["content"]
        return content, None
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_details = f"Status: {e.response.status_code}, Response: {e.response.text}"
        else:
            error_details = str(e)
        return None, f"Request failed: {error_details}"
    except KeyError as e:
        return None, f"KeyError: {str(e)} in API response"
    except Exception as e: # Captura de exceção mais genérica para robustez
        # Usar traceback aqui seria útil se não estivesse sendo removido
        # return None, f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
        return None, f"Unexpected error in _call_llm_api (brain): {str(e)}"


def generate_next_objective(
    api_key: str,
    model: str,
    current_manifest: str,
    logger: Any, # logging.Logger
    project_root_dir: str, # Novo parâmetro para o caminho raiz do projeto
    base_url: str = "https://openrouter.ai/api/v1",
    memory_summary: Optional[str] = None
) -> str:
    """
    Gera o próximo objetivo evolutivo usando um modelo leve e análise de código.
    """
    if logger: logger.info("Gerando próximo objetivo...")

    # 1. Analisar métricas do código
    code_analysis_summary_str = ""
    try:
        if logger: logger.info(f"Analisando métricas do código em: {project_root_dir}")
        # Usar "." como root_dir para analyze_code_metrics se project_root_dir for o diretório atual do Hephaestus
        # Idealmente, project_root_dir deve ser o caminho absoluto para a raiz do projeto que Hephaestus está analisando.
        # Para este exemplo, vamos assumir que o script principal (main.py) está na raiz do projeto Hephaestus,
        # e se ele estiver analisando a si mesmo, "." é apropriado.
        # Se Hephaestus analisar OUTRO projeto, project_root_dir deve apontar para esse projeto.
        # Vamos assumir que o `main.py` passa o `config.project_path` ou `os.getcwd()`

        # Definindo limiares (podem vir de configuração no futuro)
        FILE_LOC_THRESHOLD = 300
        FUNC_LOC_THRESHOLD = 50
        FUNC_CC_THRESHOLD = 10

        # Excluded patterns - pode vir da configuração do projeto também
        # Por agora, usamos os padrões default de analyze_code_metrics
        analysis_results = analyze_code_metrics(
            root_dir=project_root_dir,
            file_loc_threshold=FILE_LOC_THRESHOLD,
            func_loc_threshold=FUNC_LOC_THRESHOLD,
            func_cc_threshold=FUNC_CC_THRESHOLD
        )

        summary_data = analysis_results.get("summary", {})
        sections = []

        if summary_data.get("large_files"):
            sections.append("Arquivos Grandes (potenciais candidatos a modularização):")
            for path, loc in summary_data["large_files"]:
                sections.append(f"  - {path} (LOC: {loc})")

        if summary_data.get("large_functions"):
            sections.append("\nFunções Grandes (potenciais candidatas a refatoração/divisão):")
            for path, name, loc in summary_data["large_functions"]:
                sections.append(f"  - {path} -> {name}() (LOC: {loc})")

        if summary_data.get("complex_functions"):
            sections.append("\nFunções Complexas (alta CC, potenciais candidatas a refatoração/simplificação):")
            for path, name, cc in summary_data["complex_functions"]:
                sections.append(f"  - {path} -> {name}() (CC: {cc})")

        if summary_data.get("missing_tests"):
            sections.append("\nMódulos sem Arquivos de Teste Correspondentes (considerar criar testes):")
            for path in summary_data["missing_tests"]:
                sections.append(f"  - {path}")

        if not sections:
            code_analysis_summary_str = "Nenhuma métrica de código notável (arquivos grandes, funções complexas/grandes, ou testes ausentes) foi identificada com os limiares atuais."
        else:
            code_analysis_summary_str = "\n".join(sections)

        if logger: logger.debug(f"Resumo da análise de código:\n{code_analysis_summary_str}")

    except Exception as e:
        if logger: logger.error(f"Erro ao analisar métricas do código: {e}", exc_info=True)
        code_analysis_summary_str = "Erro ao processar a análise de código."


    # 2. Preparar contexto do manifesto e memória
    current_manifest = current_manifest or "" # Garantir que não seja None
    sanitized_memory = memory_summary.strip() if memory_summary and memory_summary.strip() else None
    memory_context_section = ""
    if sanitized_memory and sanitized_memory != "No relevant history available.":
        memory_context_section = f"""
[HISTÓRICO RECENTE DO PROJETO E DO AGENTE (Hephaestus)]
{sanitized_memory}
Considere este histórico para evitar repetir falhas, construir sobre sucessos e identificar lacunas.
"""
    # 3. Construir o prompt
    if not current_manifest.strip() and not code_analysis_summary_str.strip(): # Primeiro ciclo, sem análise
        prompt_template = """
[Contexto]
Você é o 'Planejador Estratégico' do agente de IA autônomo Hephaestus. Este é o primeiro ciclo de execução, o manifesto do projeto ainda não existe e a análise de código não retornou dados significativos. Sua tarefa é propor um objetivo inicial para criar a documentação básica do projeto ou realizar uma análise inicial.
{memory_section}
[Exemplos de Primeiros Objetivos]
- "Crie o arquivo AGENTS.md com a estrutura básica do projeto."
- "Documente as interfaces principais no manifesto do projeto."
- "Descreva a arquitetura básica do agente no manifesto."
- "Execute uma varredura inicial para identificar os principais componentes do projeto."

[Sua Tarefa]
Gere APENAS uma única string de texto contendo o objetivo inicial. Seja conciso e direto.
"""
        prompt = prompt_template.format(memory_section=memory_context_section)
    else:
        # O prompt será construído no próximo passo do plano.
        prompt_template = """
[Contexto Principal]
Você é o 'Planejador Estratégico Avançado' do agente de IA autônomo Hephaestus. Sua principal responsabilidade é identificar e propor o próximo objetivo de desenvolvimento mais impactante para a evolução do agente ou do projeto em análise.

[Processo de Decisão para o Próximo Objetivo]
1.  **Analise as Métricas de Código:** Revise a seção `[MÉTRICAS E ANÁLISE DO CÓDIGO]` abaixo. Ela contém dados sobre o tamanho dos arquivos (LOC), tamanho de funções (LOC), complexidade ciclomática (CC) de funções, e módulos que podem estar sem testes.
2.  **Considere o Manifesto do Projeto:** Se o `[MANIFESTO ATUAL DO PROJETO]` for fornecido, use-o para entender os objetivos gerais, a arquitetura e as áreas já documentadas ou que precisam de atenção.
3.  **Revise o Histórico Recente:** A seção `[HISTÓRICO RECENTE DO PROJETO E DO AGENTE]` oferece contexto sobre tarefas recentes, sucessos e falhas. Evite repetir objetivos que falharam recentemente da mesma forma, a menos que a causa da falha tenha sido resolvida. Use o histórico para construir sobre sucessos.
4.  **Priorize Melhorias Estruturais e de Qualidade:** Com base nas métricas, identifique oportunidades para:
    *   Refatorar módulos muito grandes ou funções muito longas/complexas.
    *   Criar testes para módulos ou funções críticas/complexas que não os possuem.
    *   Melhorar a documentação (docstrings, manifesto) onde for crucial.
    *   Propor a criação de novas capacidades (novos agentes, ferramentas) se a análise indicar uma necessidade estratégica.
5.  **Seja Específico e Acionável:** O objetivo deve ser claro, conciso e indicar uma ação concreta.

{memory_section}

[MÉTRICAS E ANÁLISE DO CÓDIGO]
{code_analysis_summary}

[MANIFESTO ATUAL DO PROJETO (se existente)]
{current_manifest}

[Exemplos de Objetivos Inteligentes e Autoconscientes]
*   **Refatoração Baseada em Métricas:**
    *   "Refatorar o módulo `agent/brain.py` (LOC: 350) que é extenso, considerando dividir responsabilidades em módulos menores (ex: `agent/prompt_builder.py` ou `agent/analysis_processor.py`)."
    *   "A função `generate_next_objective` em `agent/brain.py` (LOC: 85, CC: 12) é longa e complexa. Proponha um plano para refatorá-la em funções menores e mais focadas."
    *   "Analisar as funções mais complexas (CC > 10) listadas nas métricas e selecionar uma para refatoração."
*   **Criação de Testes:**
    *   "O módulo `agent/project_scanner.py` (LOC: 280) não possui um arquivo de teste `tests/agent/test_project_scanner.py`. Crie testes unitários para a função `analyze_code_metrics`."
    *   "A função `_call_llm_api` em `agent/brain.py` é crítica. Garantir que existam testes de unidade robustos para ela, cobrindo casos de sucesso e falha."
*   **Melhoria da Documentação Estratégica:**
    *   "O manifesto (`AGENTS.md`) não descreve a nova funcionalidade de análise de métricas em `project_scanner.py`. Atualize-o."
    *   "Melhorar as docstrings das funções públicas no módulo `agent/memory.py` para detalhar os parâmetros e o comportamento esperado."
*   **Desenvolvimento de Novas Capacidades (Agentes/Ferramentas):**
    *   "Criar um novo agente (ex: `CodeQualityAgent` em `agent/agents.py`) dedicado a monitorar continuamente as métricas de qualidade do código e reportar regressões."
    *   "Desenvolver uma nova ferramenta em `agent/tool_executor.py` para validar automaticamente a sintaxe de arquivos JSON antes de serem processados."
    *   "Propor um sistema para Hephaestus avaliar a performance de suas próprias operações e identificar gargalos."
*   **Objetivos Genéricos (quando métricas/manifesto são insuficientes):**
    *   "Analisar o módulo `agent/state.py` para identificar possíveis melhorias de clareza ou eficiência."
    *   "Revisar os logs recentes em busca de erros frequentes e propor um objetivo para corrigi-los."

[Sua Tarefa]
Com base em TODA a informação fornecida (métricas, manifesto, histórico), gere APENAS uma única string de texto contendo o PRÓXIMO OBJETIVO ESTRATÉGICO. O objetivo deve ser o mais impactante e lógico para a evolução do projeto neste momento.
Seja conciso, mas específico o suficiente para ser acionável.
"""
        prompt = prompt_template.format(
            memory_section=memory_context_section,
            code_analysis_summary=code_analysis_summary_str,
            current_manifest=current_manifest if current_manifest.strip() else "N/A (Manifesto não existente ou vazio)"
        )

    if logger: logger.debug(f"Prompt para generate_next_objective:\n{prompt}")

    # 4. Chamada à API LLM
    content, error = _call_llm_api(
        api_key=api_key,
        model=model,
        prompt=prompt,
        temperature=0.3,
        base_url=base_url,  # URL original sem modificações
        logger=logger
    )

    if error:
        log_message = f"Erro ao gerar próximo objetivo: {error}"
        if logger:
            logger.error(log_message)
        else:
            print(log_message)
        return "Analisar o estado atual do projeto e propor uma melhoria incremental"

    if not content:
        log_message = "Resposta vazia do LLM para próximo objetivo."
        if logger:
            logger.warn(log_message)
        else:
            print(log_message)
        return "Analisar o estado atual do projeto e propor uma melhoria incremental"

    return content.strip()


def generate_capacitation_objective(
    api_key: str,
    model: str,
    engineer_analysis: str,
    base_url: str = "https://openrouter.ai/api/v1",
    memory_summary: Optional[str] = None,
    logger: Optional[Any] = None
) -> str:
    """Gera um objetivo para criar novas capacidades necessárias."""
    # url = f"{base_url}/chat/completions" # Movido para _call_llm_api
    # headers = { ... } # Movido para _call_llm_api

    memory_context_str = ""
    if memory_summary and memory_summary.strip() and memory_summary != "No relevant history available.":
        memory_context_str = f"""
[HISTÓRICO RECENTE DO AGENTE (Hephaestus)]
{memory_summary}
Verifique se alguma capacidade similar já foi tentada ou implementada recentemente.
"""

    prompt = f"""
[Contexto]
Você é o Planejador de Capacitação do agente Hephaestus. Um engenheiro propôs uma solução que requer novas ferramentas/capacidades que não existem ou não foram suficientes anteriormente.
{memory_context_str}
[Análise do Engenheiro que Requer Nova Capacidade]
{engineer_analysis}

[Sua Tarefa]
Traduza a necessidade descrita na análise em um objetivo de engenharia claro, conciso e executável para criar ou aprimorar a capacidade que falta. O objetivo deve ser uma instrução para o próprio agente Hephaestus se modificar ou adicionar novas ferramentas/funções.
Considere o histórico para não repetir sugestões de capacitação idênticas se elas falharam ou se já foram bem-sucedidas e a análise indica uma nova necessidade.

[Exemplo de Objetivo de Capacitação]
Se a análise diz "precisamos de uma ferramenta para fazer requests web GET", seu output poderia ser: "Adicione uma nova função `http_get(url: str) -> str` ao `agent/tool_executor.py` que use a biblioteca `requests` para fazer requisições GET e retorne o conteúdo da resposta como string."
Se a análise diz "a função de parsing de JSON falhou com arquivos grandes", seu output poderia ser: "Melhore a função `parse_json_file` em `agent/utils.py` para lidar com streaming de dados ou aumentar a eficiência para arquivos JSON grandes."


[FORMATO OBRIGATÓRIO]
Gere APENAS a string de texto do novo objetivo de capacitação.
O objetivo DEVE começar com "[TAREFA DE CAPACITAÇÃO]". Por exemplo: "[TAREFA DE CAPACITAÇÃO] Adicionar nova ferramenta X."
"""
    
    if logger:
        logger.debug(f"Prompt para gerar objetivo de capacitação:\n{prompt}")

    # payload = { ... } # Movido para _call_llm_api
    content, error = _call_llm_api(api_key, model, prompt, 0.3, base_url, logger)

    if error:
        log_message = f"Erro ao gerar objetivo de capacitação: {error}"
        if logger:
            logger.error(log_message)
        else:
            print(log_message)
        return "Analisar a necessidade de capacitação e propor uma solução"

    if not content:
        log_message = "Resposta vazia do LLM para objetivo de capacitação."
        if logger:
            logger.warn(log_message)
        else:
            print(log_message)
        return "Analisar a necessidade de capacitação e propor uma solução"

    return content.strip()


def generate_commit_message(
    api_key: str,
    model: str,
    analysis_summary: str,
    objective: str,
    logger: Any, # logging.Logger
    base_url: str = "https://openrouter.ai/api/v1"
) -> str:
    """
    Gera uma mensagem de commit concisa e informativa usando um LLM.

    Args:
        api_key: Chave API (ex: OpenRouter).
        model: Modelo LLM a ser usado.
        analysis_summary: Resumo da análise e implementação da mudança.
        objective: O objetivo original da mudança.
        logger: Instância do logger para registrar informações.
        base_url: URL base da API LLM.

    Returns:
        Uma string contendo a mensagem de commit gerada.
        Retorna uma mensagem de fallback em caso de erro.
    """
    prompt = f"""
[Contexto] Você é um engenheiro de software escrevendo uma mensagem de commit para uma mudança que acabou de ser validada e aplicada.
[Objetivo da Mudança]
{objective}
[Análise/Resumo da Implementação]
{analysis_summary}
[Sua Tarefa]
Com base no objetivo e na análise, escreva uma mensagem de commit clara e concisa seguindo o padrão 'Conventional Commits'. Ex: feat: Adiciona ferramenta de benchmark ou fix: Corrige validação de sintaxe para JSON. A mensagem deve ser apenas a string do commit, sem prefixos ou explicações.
"""

    logger.info(f"Gerando mensagem de commit com o modelo: {model}...")

    # Simulação da chamada à API LLM, pois não temos acesso real neste ambiente.
    # Em um ambiente real, usaríamos _call_llm_api ou uma função similar.
    # Para este exercício, vamos construir uma mensagem de commit baseada nos inputs.
    # Isso também evita a necessidade de ter uma API_KEY configurada para esta etapa.

    # Heurística para determinar o tipo de commit
    commit_type = "feat"  # Padrão para novos recursos
    objective_lower = objective.lower()
    
    # Primeiro verificamos palavras-chave específicas para feat
    if any(word in objective_lower for word in ["funcionalidade", "feature", "nova capacidade", "novo recurso"]):
        commit_type = "feat"
    elif "fix" in objective_lower or "corrigir" in objective_lower or "bug" in objective_lower:
        commit_type = "fix"
    elif "refactor" in objective_lower or "refatorar" in objective_lower:
        commit_type = "refactor"
    elif "doc" in objective_lower or "documentar" in objective_lower:
        commit_type = "docs"
    elif "test" in objective_lower or "teste" in objective_lower:
        commit_type = "test"
    elif "build" in objective_lower or "ci" in objective_lower or "config" in objective_lower:
        commit_type = "build"
    elif "chore" in objective_lower or "manutenção" in objective_lower or "limpeza" in objective_lower:
        commit_type = "chore"

    # Simplificando o corpo da mensagem de commit para este exemplo
    # Removemos quebras de linha e limitamos o tamanho para o resumo do objetivo.
    short_objective = objective.replace('\n', ' ').replace('\r', '')
    if len(short_objective) > 70: # Limite arbitrário para o resumo
        short_objective = short_objective[:67] + "..."

    # Fallback para uma mensagem de commit se a chamada LLM (simulada) falhar.
    # No nosso caso, a simulação sempre "funciona".
    simulated_commit_message = f"{commit_type}: {short_objective}"

    logger.info(f"Mensagem de commit gerada (simulada): {simulated_commit_message}")
    return simulated_commit_message

    # Código original que chamaria a LLM (mantido comentado para referência):
    # content, error = _call_llm_api(api_key, model, prompt, 0.5, base_url, logger)
    # if error:
    #     logger.error(f"Erro ao gerar mensagem de commit: {error}")
    #     # Fallback para uma mensagem de commit genérica
    #     return f"chore: Atualizações automáticas baseadas no objetivo: {objective}"
    # if not content:
    #     logger.warn("Resposta vazia do LLM para mensagem de commit.")
    #     return f"chore: Atualizações automáticas (resposta LLM vazia): {objective}"
    #
    # # A LLM deve retornar apenas a mensagem de commit.
    # return content.strip()
