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
    base_url: str = "https://openrouter.ai/api/v1"
) -> str:
    """
    Gera o próximo objetivo evolutivo usando um modelo leve.
    
    Args:
        api_key: Chave API do OpenRouter
        model: Modelo a ser usado (ex: "anthropic/claude-3.5-haiku")
        current_manifest: Conteúdo atual do manifesto do projeto
        
    Returns:
        String com o próximo objetivo evolutivo
    """
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    if not current_manifest.strip():
        # Special case for first run when no manifest exists
        prompt = """
[Contexto]
Você é o 'Planejador Estratégico' do agente de IA autônomo Hephaestus. Este é o primeiro ciclo de execução e o manifesto do projeto ainda não existe. Sua tarefa é propor um objetivo inicial para criar a documentação básica do projeto.

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
Você é o 'Planejador Estratégico' do agente de IA autônomo Hephaestus. Sua única função é analisar o estado atual do projeto (descrito no manifesto abaixo) e propor o próximo objetivo lógico e incremental para a evolução do agente. O objetivo deve ser uma tarefa pequena, segura e que melhore a qualidade, performance ou capacidade do sistema.

[Exemplos de Bons Objetivos]
- "Remova os imports não usados no arquivo X."
- "A docstring da função Y no arquivo Z está incompleta. Melhore-a."
- "A complexidade da função A no módulo B é alta. Refatore-a em funções menores."
- "O arquivo de configuração não possui descrições para a estratégia Y. Adicione-as."
- "Crie testes em pytest para a função Z, que atualmente não tem cobertura de testes."

[Manifesto Atual do Projeto]
{current_manifest}

[Sua Tarefa]
Gere APENAS uma única string de texto contendo o próximo objetivo. Seja conciso e direto.
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
    base_url: str = "https://openrouter.ai/api/v1"
) -> str:
    """Gera um objetivo para criar novas capacidades necessárias.
    
    Args:
        api_key: Chave API do OpenRouter
        model: Modelo a ser usado (ex: "anthropic/claude-3.5-haiku")
        engineer_analysis: Análise do Engenheiro indicando a necessidade
        
    Returns:
        String com o objetivo de capacitação
    """
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
[Contexto]
Você é o Planejador de Capacitação do agente Hephaestus. Um engenheiro propôs uma solução que requer novas ferramentas que não existem.

[Análise do Engenheiro que Requer Nova Capacidade]
{engineer_analysis}

[Sua Tarefa]
Traduza a necessidade descrita acima em um objetivo de engenharia claro, conciso e executável para criar a capacidade que falta. O objetivo deve ser uma instrução para o próprio agente se modificar.

[Exemplo]
Se a análise diz "precisamos de uma ferramenta para fazer requests web", seu output deve ser "Adicione uma nova função `http_get` ao `tool_executor.py` que use a biblioteca `requests` para fazer requisições web e retorne o conteúdo."

Gere APENAS a string de texto do novo objetivo.
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
        print(f"Erro ao gerar objetivo de capacitação: {str(e)}")
        return "Analisar a necessidade de capacitação e propor uma solução"


def get_maestro_decision(
    api_key: str,
    model_list: List[str],
    engineer_response: Dict[str, Any],
    config: Dict[str, Any],
    base_url: str = "https://openrouter.ai/api/v1",
) -> List[Dict[str, Any]]:
    """Consulta a LLM para decidir qual estratégia de validação adotar."""

    attempt_logs = []
    available_keys = ", ".join(config.get("validation_strategies", {}).keys())
    engineer_summary = json.dumps(engineer_response, ensure_ascii=False, indent=2)

    for model in model_list:
        print(f"Tentando com o modelo: {model} para decisão do Maestro...")
        url = f"{base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        prompt = f"""
[IDENTIDADE]
Você é o Maestro do agente Hephaestus. Analise a proposta do Engenheiro abaixo e decida a melhor ação:
1. Se a solução requer novas capacidades (ferramentas, estratégias ou bibliotecas), responda com CAPACITATION_REQUIRED
2. Caso contrário, escolha a estratégia de validação mais adequada

Estratégias disponíveis: {available_keys}, CAPACITATION_REQUIRED

Proposta do Engenheiro:
{engineer_summary}

Responda apenas com um JSON no formato:
{{"strategy_key": "<UMA_DAS_CHAVES_ACIMA_OU_CAPACITATION_REQUIRED>"}}
"""

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
                continue
                
            attempt_log["parsed_json"] = parsed
            attempt_log["success"] = True
        except Exception as e:
            attempt_log["raw_response"] = f"Erro na decisão do Maestro: {str(e)}"

        attempt_logs.append(attempt_log)

    return attempt_logs
