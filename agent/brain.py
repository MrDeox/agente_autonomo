import json
import requests
import traceback # Mantido para uso potencial em tratamento de erros, embora não usado diretamente nas novas funções.
from typing import Optional, Dict, Any, List, Tuple # Tuple não é usado, mas pode ser mantido por enquanto.

# Funções de comunicação com API (simuladas/reutilizadas)
# Idealmente, haveria uma função genérica para chamadas de API para evitar duplicação.

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
        logger.debug(f"API Response: {response_json}")  # Log da resposta completa
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
    except Exception as e:
        return None, f"Unexpected error: {str(e)}\n{traceback.format_exc()}"

def get_action_plan(
    api_key: str,
    model: str, # Modelo para o Arquiteto
    objective: str,
    manifest: str,
    logger: Any, # logging.Logger, mas Any para evitar import circular se brain for importado em main typings
    base_url: str = "https://openrouter.ai/api/v1"
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Fase 2 (Arquiteto): Pega o objetivo e o manifesto, e retorna um plano de patches em JSON.
    Retorna um dicionário com os patches ou None em caso de erro, mais uma mensagem de erro.
    O Arquiteto agora gera os patches diretamente, incluindo o conteúdo.
    """
    prompt = f"""
Você é o Arquiteto de Software do agente Hephaestus. Sua tarefa é pegar o objetivo de alto nível e, com base no manifesto do projeto, criar um plano de patches JSON para modificar os arquivos.

[OBJETIVO]
{objective}

[MANIFESTO DO PROJETO]
{manifest}

[SUA TAREFA]
Crie um plano JSON com uma lista de "patches" para aplicar. Cada patch DEVE incluir o conteúdo completo a ser inserido ou que substituirá um bloco.
As operações válidas para cada patch são: "INSERT", "REPLACE", "DELETE_BLOCK".
Para operações em arquivos existentes, analise o manifesto para entender o estado atual do arquivo antes de propor o patch.
Se um arquivo não existe e a operação é "INSERT" ou "REPLACE" (com "block_to_replace": null), o arquivo será criado.

[FORMATO DE SAÍDA OBRIGATÓRIO]
Sua resposta DEVE ser um objeto JSON válido e nada mais.
{{
  "analysis": "Sua análise e raciocínio para o plano de patches.",
  "patches_to_apply": [ // MODIFICADO de action_plan para patches_to_apply
    {{
      "file_path": "caminho/do/arquivo.py",
      "operation": "INSERT",
      "line_number": 1, // Opcional. 1-based. Se omitido ou > num_linhas, insere no final.
      "content": "import os\\nimport sys" // Conteúdo real a ser inserido. Newlines como \\n.
    }},
    {{
      "file_path": "caminho/existente/arquivo.txt",
      "operation": "REPLACE",
      "block_to_replace": "texto antigo a ser substituído", // String exata ou um padrão regex.
                                                              // Se null, o arquivo inteiro é substituído (ou criado se não existir).
      "is_regex": false, // Opcional, default false. True se block_to_replace for um regex.
      "content": "novo texto que substitui o bloco antigo."
    }},
    {{
      "file_path": "caminho/outro_arquivo.py",
      "operation": "DELETE_BLOCK",
      "block_to_delete": "def funcao_obsoleta(param):\\n    pass\\n", // String exata do bloco a deletar, incluindo newlines.
                                                                     // Ou um padrão regex.
      "is_regex": false // Opcional.
    }},
    {{ // Exemplo de criação de novo arquivo usando REPLACE (block_to_replace: null)
      "file_path": "novo/arquivo_config.json",
      "operation": "REPLACE",
      "block_to_replace": null, // Essencial para criar/sobrescrever arquivo inteiro
      "content": "{{\\n  \\"key\\": \\"value\\",\\n  \\"another_key\\": 123\\n}}"
    }}
  ]
}}

[INSTRUÇÕES IMPORTANTES PARA O CONTEÚDO DO PATCH]
- Para "INSERT" e "REPLACE", o campo "content" DEVE conter o código/texto REAL e COMPLETO a ser usado.
- Newlines dentro do "content" DEVEM ser representados como '\\n'.
- Para "DELETE_BLOCK", o "block_to_delete" deve ser a string exata do bloco a ser removido, incluindo newlines se elas fazem parte do bloco e devem ser removidas. Se for um regex, ele deve casar o bloco.
- Para "REPLACE" de arquivo inteiro ou criação de novo arquivo, use "block_to_replace": null.
- Certifique-se de que o JSON gerado é estritamente válido. Escape caracteres especiais dentro das strings JSON conforme necessário (ex: '\\\\n' para newline, '\\\\"' para aspas).
"""
    logger.info(f"Gerando plano de patches com o modelo: {model}...")
    raw_response, error = _call_llm_api(api_key, model, prompt, 0.4, base_url, logger) # Temp um pouco mais baixa

    if error:
        logger.error(f"Erro ao chamar LLM para plano de patches: {error}")
        return None, f"Erro ao chamar LLM para plano de patches: {error}"
    if not raw_response:
        logger.error("Resposta vazia do LLM para plano de patches.")
        return None, "Resposta vazia do LLM para plano de patches."

    try:
        clean_content = raw_response.strip()
        logger.debug(f"Raw response before cleaning: {raw_response[:200]}...")  # Log parcial
        
        # Find the first { and last } to extract just the JSON part
        first_brace = clean_content.find('{')
        last_brace = clean_content.rfind('}')
        
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            clean_content = clean_content[first_brace:last_brace+1]
            logger.debug(f"Extracted JSON content: {clean_content[:200]}...")  # Log parcial
        else:
            # Fallback to original cleaning if braces not found
            if clean_content.startswith('```json'):
                clean_content = clean_content[7:].strip()
                if clean_content.endswith('```'):
                    clean_content = clean_content[:-3].strip()
            elif clean_content.startswith('```'):
                clean_content = clean_content[3:].strip()
                if clean_content.endswith('```'):
                    clean_content = clean_content[:-3].strip()
        
        # Remove control characters that might break JSON parsing
        clean_content = ''.join(char for char in clean_content if ord(char) >= 32 or char in '\n\r\t')
        logger.debug(f"Final cleaned content before parsing: {clean_content[:200]}...")  # Log parcial
        
        parsed_json = json.loads(clean_content)

        if "patches_to_apply" not in parsed_json or not isinstance(parsed_json["patches_to_apply"], list):
            logger.error("JSON do plano de patches não contém 'patches_to_apply' ou não é uma lista.")
            return None, "JSON do plano de patches não contém a chave 'patches_to_apply' ou não é uma lista."

        # Validação mais detalhada de cada patch (opcional, mas bom)
        for i, patch in enumerate(parsed_json["patches_to_apply"]):
            if not isinstance(patch, dict):
                err_msg = f"Patch na posição {i} não é um dicionário."
                logger.error(err_msg)
                return None, err_msg
            if "file_path" not in patch or "operation" not in patch:
                err_msg = f"Patch na posição {i} não tem 'file_path' ou 'operation'."
                logger.error(err_msg)
                return None, err_msg
            if patch["operation"] in ["INSERT", "REPLACE"] and "content" not in patch:
                err_msg = f"Patch {patch['operation']} na posição {i} para '{patch['file_path']}' não tem 'content'."
                logger.error(err_msg)
                return None, err_msg
            if patch["operation"] == "DELETE_BLOCK" and "block_to_delete" not in patch:
                err_msg = f"Patch DELETE_BLOCK na posição {i} para '{patch['file_path']}' não tem 'block_to_delete'."
                logger.error(err_msg)
                return None, err_msg
            if patch["operation"] == "REPLACE" and "block_to_replace" not in patch: # block_to_replace pode ser null
                err_msg = f"Patch REPLACE na posição {i} para '{patch['file_path']}' não tem 'block_to_replace' (pode ser null)."
                logger.error(err_msg)
                return None, err_msg


        return parsed_json, None
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON do plano de patches: {str(e)}. Resposta: {raw_response[:500]}...")
        return None, f"Erro ao decodificar JSON do plano de patches: {str(e)}. Resposta: {raw_response}"
    except Exception as e:
        logger.error(f"Erro inesperado ao processar plano de patches: {str(e)}", exc_info=True)
        return None, f"Erro inesperado ao processar plano de patches: {str(e)}"


# A função generate_code_for_action foi removida pois o Arquiteto agora gera patches com conteúdo diretamente.

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
    
    Args:
        api_key: Chave API do OpenRouter
        model: Modelo a ser usado (ex: "anthropic/claude-3.5-haiku")
        current_manifest: Conteúdo atual do manifesto do projeto
        logger: Instância do logger.
        base_url: URL base da API LLM.
        memory_summary: Resumo do histórico de memória do agente.
        
    Returns:
        String com o próximo objetivo evolutivo
    """
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    memory_context_str = ""
    if memory_summary and memory_summary.strip() and memory_summary != "No relevant history available.":
        memory_context_str = f"""
[HISTÓRICO RECENTE DO PROJETO E DO AGENTE (Hephaestus)]
{memory_summary}
Considere este histórico para evitar repetir falhas, construir sobre sucessos e identificar lacunas.
"""

    if not current_manifest.strip():
        # Special case for first run when no manifest exists
        prompt = f"""
[Contexto]
Você é o 'Planejador Estratégico' do agente de IA autônomo Hephaestus. Este é o primeiro ciclo de execução e o manifesto do projeto ainda não existe. Sua tarefa é propor um objetivo inicial para criar a documentação básica do projeto.
{memory_context_str}
[Exemplos de Primeiros Objetivos]
- "Crie o arquivo AGENTS.md com a estrutura básica do projeto."
- "Documente as interfaces principais no manifesto do projeto."
- "Descreva a arquitetura básica do agente no manifesto."

[Sua Tarefa]
Gere APENAS uma única string de texto contendo o objetivo inicial. Seja conciso e direto.
"""
    else:
        prompt = f"""
[Contexto]
Você é o 'Planejador Estratégico' do agente de IA autônomo Hephaestus. Sua única função é analisar o estado atual do projeto (descrito no manifesto abaixo) e o histórico recente, e então propor o próximo objetivo lógico e incremental para a evolução do agente. O objetivo deve ser uma tarefa pequena, segura e que melhore a qualidade, performance ou capacidade do sistema.
{memory_context_str}
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
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return content.strip()
    except Exception as e:
        print(f"Erro ao gerar próximo objetivo: {str(e)}")
        return "Analisar o estado atual do projeto e propor uma melhoria incremental"


def generate_capacitation_objective(
    api_key: str,
    model: str,
    engineer_analysis: str,
    base_url: str = "https://openrouter.ai/api/v1",
    memory_summary: Optional[str] = None,
    logger: Optional[Any] = None # Adicionado logger para consistência e debug
) -> str:
    """Gera um objetivo para criar novas capacidades necessárias.
    
    Args:
        api_key: Chave API do OpenRouter
        model: Modelo a ser usado (ex: "anthropic/claude-3.5-haiku")
        engineer_analysis: Análise do Engenheiro indicando a necessidade
        base_url: URL base da API LLM.
        memory_summary: Resumo do histórico de memória do agente.
        logger: Instância do logger.
        
    Returns:
        String com o objetivo de capacitação
    """
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

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

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return content.strip()
    except Exception as e:
        print(f"Erro ao gerar objetivo de capacitação: {str(e)}")
        return "Analisar a necessidade de capacitação e propor uma solução"


def get_maestro_decision(
    api_key: str,
    model_list: List[str],
    engineer_response: Dict[str, Any],
    config: Dict[str, Any],
    base_url: str = "https://openrouter.ai/api/v1",
    memory_summary: Optional[str] = None,
    logger: Optional[Any] = None # Adicionado logger para consistência e debug
) -> List[Dict[str, Any]]:
    """Consulta a LLM para decidir qual estratégia de validação adotar."""

    attempt_logs = []
    available_keys = ", ".join(config.get("validation_strategies", {}).keys())
    engineer_summary = json.dumps(engineer_response, ensure_ascii=False, indent=2)

    memory_context_str = ""
    if memory_summary and memory_summary.strip() and memory_summary != "No relevant history available.":
        memory_context_str = f"""
[HISTÓRICO RECENTE (OBJETIVOS E ESTRATÉGIAS USADAS)]
{memory_summary}
Considere este histórico ao tomar sua decisão. Evite repetir estratégias que falharam recentemente para objetivos semelhantes, a menos que a causa da falha pareça ter sido resolvida ou a proposta atual seja significativamente diferente.
"""

    for model in model_list:
        if logger:
            logger.info(f"Tentando com o modelo: {model} para decisão do Maestro...")
        else:
            print(f"Tentando com o modelo: {model} para decisão do Maestro...")

        url = f"{base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        prompt = f"""
[IDENTIDADE]
Você é o Maestro do agente Hephaestus. Sua tarefa é analisar a proposta do Engenheiro (plano de patches) e o histórico recente do agente para decidir a melhor ação a seguir.

[CONTEXTO E HISTÓRICO]
{memory_context_str}

[PROPOSTA DO ENGENHEIRO (PLANO DE PATCHES)]
{engineer_summary}

[SUA DECISÃO]
Com base na proposta do Engenheiro e no histórico:
1. Se a solução parece razoável e não requer novas capacidades fundamentais que o agente Hephaestus não possui, escolha a estratégia de validação mais adequada dentre as disponíveis.
2. Se a solução proposta pelo Engenheiro claramente requer novas capacidades (novas ferramentas, acesso a novas bibliotecas, novas estratégias de validação complexas que não existem) que o agente Hephaestus precisa desenvolver internamente, responda com `CAPACITATION_REQUIRED`.

Estratégias de Validação Disponíveis: {available_keys}
Opção Adicional: CAPACITATION_REQUIRED

[FORMATO DE SAÍDA OBRIGATÓRIO]
Responda APENAS com um objeto JSON contendo a chave "strategy_key" e o valor sendo UMA das estratégias de validação disponíveis OU "CAPACITATION_REQUIRED".
Exemplo: {{"strategy_key": "sandbox_pytest_validation"}}
Exemplo: {{"strategy_key": "CAPACITATION_REQUIRED"}}
"""
        if logger:
            logger.debug(f"Prompt para decisão do Maestro:\n{prompt}")

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }

        attempt_log = {
            "model": model,
            "raw_response": "",
            "parsed_json": None,
            "success": False,
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            response_json = response.json()
            print(f"API Response: {response_json}")  # Debug
            
            if "choices" not in response_json:
                attempt_log["raw_response"] = f"API response missing 'choices' key: {response_json}"
                attempt_logs.append(attempt_log)
                continue
                
            content = response_json["choices"][0]["message"]["content"]
            attempt_log["raw_response"] = content
            print(f"Raw content: {content}")  # Debug

            clean_content = content.strip()
            print(f"Initial clean content: {clean_content[:200]}...")  # Debug parcial
            
            # Try to find JSON between first { and last }
            first_brace = clean_content.find('{')
            last_brace = clean_content.rfind('}')
            
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                clean_content = clean_content[first_brace:last_brace+1]
                print(f"Extracted JSON: {clean_content[:200]}...")  # Debug parcial
            else:
                # Fallback to original cleaning
                if clean_content.startswith('```json'):
                    clean_content = clean_content[7:].strip()
                    if clean_content.endswith('```'):
                        clean_content = clean_content[:-3].strip()
                elif clean_content.startswith('```'):
                    clean_content = clean_content[3:].strip()
                    if clean_content.endswith('```'):
                        clean_content = clean_content[:-3].strip()

            # Remove any non-printable characters except newlines and tabs
            clean_content = ''.join(char for char in clean_content if ord(char) >= 32 or char in '\n\r\t')
            print(f"Final clean content: {clean_content[:200]}...")  # Debug parcial

            parsed = json.loads(clean_content)
            if not isinstance(parsed, dict) or "strategy_key" not in parsed:
                attempt_log["raw_response"] = f"Invalid JSON format or missing strategy_key: {parsed}"
                # BUG FIX: Append before continue if this is the path taken
                attempt_logs.append(attempt_log)
                continue
                
            attempt_log["parsed_json"] = parsed
            attempt_log["success"] = True
        except Exception as e:
            attempt_log["raw_response"] = f"Erro na decisão do Maestro: {str(e)}"
            # success is already False by default in attempt_log

        attempt_logs.append(attempt_log)

    return attempt_logs


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

    # Heurística simples para determinar o tipo de commit (feat, fix, chore, etc.)
    commit_type = "feat" # Padrão
    if "fix" in objective.lower() or "corrigir" in objective.lower() or "bug" in objective.lower():
        commit_type = "fix"
    elif "refactor" in objective.lower() or "refatorar" in objective.lower():
        commit_type = "refactor"
    elif "doc" in objective.lower() or "documentar" in objective.lower():
        commit_type = "docs"
    elif "test" in objective.lower() or "teste" in objective.lower():
        commit_type = "test"
    elif "build" in objective.lower() or "ci" in objective.lower() or "config" in objective.lower():
        commit_type = "build"
    elif "chore" in objective.lower() or "manutenção" in objective.lower() or "limpeza" in objective.lower():
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
