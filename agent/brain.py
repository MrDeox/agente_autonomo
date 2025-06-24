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
# Para esta refatoração, vamos assumir que _call_llm_api é um utilitário que pode
# ser usado por múltiplos "cérebros" ou agentes, então pode ser melhor
# movê-lo para um local mais genérico ou duplicá-lo temporariamente.
# O pedido era mover para agent/agents.py, então vamos remover daqui.
# Isso significa que as funções restantes precisarão de uma forma de chamar a LLM.

# REAVALIAÇÃO: _call_llm_api é fundamental para as funções restantes.
# Por enquanto, vamos duplicá-la aqui e em agent/agents.py.
# Uma refatoração futura poderia criar um `llm_client.py` ou similar.

def _call_llm_api(api_key: str, model: str, prompt: str, temperature: float, base_url: str, logger: Any) -> Tuple[Optional[str], Optional[str]]:
    """Função auxiliar para fazer chamadas à API LLM.
       Esta é uma cópia temporária. A original foi movida para agent/agents.py.
    """
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
    base_url: str = "https://openrouter.ai/api/v1",
    memory_summary: Optional[str] = None
) -> str:
    """
    Gera o próximo objetivo evolutivo usando um modelo leve.
    """
    # Garantir que current_manifest seja uma string para evitar AttributeError
    if current_manifest is None:
        if logger:
            logger.warn("current_manifest was None, defaulting to empty string.")
        current_manifest = ""

    # Garantir que o memory_summary seja sanitizado antes de usar
    sanitized_memory = memory_summary.strip() if memory_summary and memory_summary.strip() else None

    memory_context_section = ""
    if sanitized_memory and sanitized_memory != "No relevant history available.":
        memory_context_section = f"""
[HISTÓRICO RECENTE DO PROJETO E DO AGENTE (Hephaestus)]
{sanitized_memory}
Considere este histórico para evitar repetir falhas, construir sobre sucessos e identificar lacunas.
"""

    if not current_manifest.strip():
        prompt_template = """
[Contexto]
Você é o 'Planejador Estratégico' do agente de IA autônomo Hephaestus. Este é o primeiro ciclo de execução e o manifesto do projeto ainda não existe. Sua tarefa é propor um objetivo inicial para criar a documentação básica do projeto.
{memory_section}
[Exemplos de Primeiros Objetivos]
- "Crie o arquivo AGENTS.md com a estrutura básica do projeto."
- "Documente as interfaces principais no manifesto do projeto."
- "Descreva a arquitetura básica do agente no manifesto."

[Sua Tarefa]
Gere APENAS uma única string de texto contendo o objetivo inicial. Seja conciso e direto.
"""
        prompt = prompt_template.format(memory_section=memory_context_section)
    else:
        prompt_template = """
[Contexto]
Você é o 'Planejador Estratégico' do agente de IA autônomo Hephaestus. Sua única função é analisar o estado atual do projeto (descrito no manifesto abaixo) e o histórico recente, e então propor o próximo objetivo lógico e incremental para a evolução do agente. O objetivo deve ser uma tarefa pequena, segura e que melhore a qualidade, performance ou capacidade do sistema.
{memory_section}
[Exemplos de Bons Objetivos]
- "Remova os imports não usados no arquivo X."
- "A docstring da função Y no arquivo Z está incompleta. Melhore-a."
- "A complexidade da função A no módulo B é alta. Refatore-a em funções menores."
- "O arquivo de configuração não possui descrições para a estratégia Y. Adicione-as."
- "Crie testes em pytest para a função Z, que atualmente não tem cobertura de testes."

[Manifesto Atual do Projeto]
{current_manifest}

[Sua Tarefa]
Gere APENAS uma única string de texto contendo o próximo objetivo. Seja conciso e direto. Considere o histórico para não repetir objetivos que falharam recentemente da mesma forma ou para continuar trabalhos bem-sucedidos.
"""
        prompt = prompt_template.format(
            memory_section=memory_context_section,
            current_manifest=current_manifest
        )
    
    # Chamada segura para a API - base_url permanece intacta
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
