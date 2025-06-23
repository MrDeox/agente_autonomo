import json
import logging
import requests
# import traceback # Removido pois não é utilizado
from typing import Optional, Dict, Any, List, Tuple

# Esta função é uma cópia de agent.brain.parse_json_response
# Idealmente, seria movida para um módulo de utilitários compartilhado se usada em mais lugares.
def parse_json_response(raw_str: str, logger: Any) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Analisa uma string bruta que se espera conter JSON, limpando-a e decodificando-a.
    Remove blocos de markdown, extrai conteúdo entre a primeira '{' e a última '}',
    remove caracteres não imprimíveis e carrega o JSON.

    Args:
        raw_str: A string bruta da resposta da LLM.
        logger: Instância do logger para registrar o processo.

    Returns:
        Uma tupla contendo o dicionário JSON parseado (ou None em caso de erro)
        e uma mensagem de erro (ou None em caso de sucesso).
    """
    if not raw_str or not raw_str.strip():
        if logger: logger.error("parse_json_response: Recebeu string vazia ou apenas com espaços.")
        else: print("parse_json_response: Recebeu string vazia ou apenas com espaços.")
        return None, "String de entrada vazia ou apenas com espaços."

    clean_content = raw_str.strip()
    if logger: logger.debug(f"parse_json_response: Raw response before cleaning: {raw_str[:300]}...")

    first_brace = clean_content.find('{')
    last_brace = clean_content.rfind('}')

    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        clean_content = clean_content[first_brace:last_brace+1]
        if logger: logger.debug(f"parse_json_response: Extracted JSON content based on braces: {clean_content[:300]}...")
    else:
        if clean_content.startswith('```json'):
            clean_content = clean_content[7:].strip()
            if clean_content.endswith('```'):
                clean_content = clean_content[:-3].strip()
        elif clean_content.startswith('```'):
            clean_content = clean_content[3:].strip()
            if clean_content.endswith('```'):
                clean_content = clean_content[:-3].strip()
        if logger: logger.debug(f"parse_json_response: Content after attempting markdown removal (if any): {clean_content[:300]}...")

    clean_content = ''.join(char for char in clean_content if ord(char) >= 32 or char in ['\n', '\r', '\t'])
    if logger: logger.debug(f"parse_json_response: Final cleaned content before parsing: {clean_content[:300]}...")

    if not clean_content:
        if logger: logger.error("parse_json_response: Conteúdo ficou vazio após limpeza.")
        else: print("parse_json_response: Conteúdo ficou vazio após limpeza.")
        return None, "Conteúdo ficou vazio após limpeza."

    try:
        parsed_json = json.loads(clean_content)
        return parsed_json, None
    except json.JSONDecodeError as e:
        error_message = f"Erro ao decodificar JSON: {str(e)}. Conteúdo limpo (parcial): {clean_content[:500]}"
        if logger: logger.error(f"parse_json_response: {error_message}. Resposta original (parcial): {raw_str[:200]}")
        else: print(f"parse_json_response: {error_message}. Resposta original (parcial): {raw_str[:200]}")
        return None, f"Erro ao decodificar JSON: {str(e)}. Resposta original (parcial): {raw_str[:200]}"
    except Exception as e:
        error_message = f"Erro inesperado durante o parsing do JSON: {str(e)}"
        if logger: logger.error(f"parse_json_response: {error_message}\n{traceback.format_exc()}", exc_info=True)
        else: print(f"parse_json_response: {error_message}\n{traceback.format_exc()}")
        return None, f"Erro inesperado durante o parsing do JSON: {str(e)}"

# Esta função é uma cópia de agent.brain._call_llm_api
# Idealmente, seria movida para um módulo de utilitários compartilhado ou uma classe base de API.
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
        if logger: logger.debug(f"API Response: {response_json}")
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


class ArchitectAgent:
    def __init__(self, api_key: str, model: str, logger: Any, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.model = model
        self.logger = logger
        self.base_url = base_url

    def plan_action(self, objective: str, manifest: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Encapsula a lógica de get_action_plan.
        Gera um plano de patches JSON com base no objetivo e no manifesto.
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
  "patches_to_apply": [
    {{
      "file_path": "caminho/do/arquivo.py",
      "operation": "INSERT",
      "line_number": 1,
      "content": "import os\\nimport sys"
    }},
    {{
      "file_path": "caminho/existente/arquivo.txt",
      "operation": "REPLACE",
      "block_to_replace": "texto antigo a ser substituído",
      "is_regex": false,
      "content": "novo texto que substitui o bloco antigo."
    }},
    {{
      "file_path": "caminho/outro_arquivo.py",
      "operation": "DELETE_BLOCK",
      "block_to_delete": "def funcao_obsoleta(param):\\n    pass\\n",
      "is_regex": false
    }},
    {{
      "file_path": "novo/arquivo_config.json",
      "operation": "REPLACE",
      "block_to_replace": null,
      "content": "{{\\n  \\"key\\": \\"value\\",\\n  \\"another_key\\": 123\\n}}"
    }}
  ]
}}

[INSTRUÇÕES IMPORTANTES PARA O CONTEÚDO DO PATCH]
- Para "INSERT" e "REPLACE", o campo "content" DEVE conter o código/texto REAL e COMPLETO a ser usado.
- Newlines dentro do "content" DEVEM ser representados como '\\n'.
- Para "DELETE_BLOCK", o "block_to_delete" deve ser a string exata do bloco a ser removido.
- Para "REPLACE" de arquivo inteiro ou criação de novo arquivo, use "block_to_replace": null.
- Certifique-se de que o JSON gerado é estritamente válido.
"""
        self.logger.info(f"ArchitectAgent: Gerando plano de patches com o modelo: {self.model}...")
        raw_response, error = _call_llm_api(self.api_key, self.model, prompt, 0.4, self.base_url, self.logger)

        if error:
            self.logger.error(f"ArchitectAgent: Erro ao chamar LLM para plano de patches: {error}")
            return None, f"Erro ao chamar LLM para plano de patches: {error}"

        if not raw_response: # Adicionado para tratar resposta vazia antes do parse
            self.logger.error("ArchitectAgent: Resposta vazia do LLM para plano de patches.")
            return None, "Resposta vazia do LLM para plano de patches."

        parsed_json, error_parsing = parse_json_response(raw_response, self.logger)

        if error_parsing:
            self.logger.error(f"ArchitectAgent: Erro ao fazer parse do JSON do plano de patches: {error_parsing}")
            return None, f"Erro ao fazer parse do JSON do plano de patches: {error_parsing}"

        if not parsed_json:
            self.logger.error("ArchitectAgent: JSON do plano de patches resultou em None sem erro de parsing explícito.")
            return None, "JSON do plano de patches resultou em None."

        if not isinstance(parsed_json, dict) or "patches_to_apply" not in parsed_json or \
           not isinstance(parsed_json.get("patches_to_apply"), list):
            self.logger.error("ArchitectAgent: JSON do plano de patches inválido ou não contém 'patches_to_apply' como uma lista.")
            return None, "JSON do plano de patches inválido ou não contém a chave 'patches_to_apply' como uma lista."

        for i, patch in enumerate(parsed_json.get("patches_to_apply", [])):
            if not isinstance(patch, dict):
                err_msg = f"ArchitectAgent: Patch na posição {i} não é um dicionário."
                self.logger.error(err_msg)
                return None, err_msg
            if "file_path" not in patch or "operation" not in patch:
                err_msg = f"ArchitectAgent: Patch na posição {i} não tem 'file_path' ou 'operation'."
                self.logger.error(err_msg)
                return None, err_msg
            if patch["operation"] in ["INSERT", "REPLACE"] and "content" not in patch:
                err_msg = f"ArchitectAgent: Patch {patch['operation']} na posição {i} para '{patch['file_path']}' não tem 'content'."
                self.logger.error(err_msg)
                return None, err_msg
            if patch["operation"] == "DELETE_BLOCK" and "block_to_delete" not in patch:
                err_msg = f"ArchitectAgent: Patch DELETE_BLOCK na posição {i} para '{patch['file_path']}' não tem 'block_to_delete'."
                self.logger.error(err_msg)
                return None, err_msg
            if patch["operation"] == "REPLACE" and "block_to_replace" not in patch:
                err_msg = f"ArchitectAgent: Patch REPLACE na posição {i} para '{patch['file_path']}' não tem 'block_to_replace' (pode ser null)."
                self.logger.error(err_msg)
                return None, err_msg

        return parsed_json, None


class MaestroAgent:
    def __init__(self, api_key: str, model_list: List[str], config: Dict[str, Any], logger: Any, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.model_list = model_list
        self.config = config
        self.logger = logger
        self.base_url = base_url

    def choose_strategy(self, action_plan_data: Dict[str, Any], memory_summary: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Encapsula a lógica de get_maestro_decision.
        Consulta a LLM para decidir qual estratégia de validação adotar.
        """
        attempt_logs = []
        available_keys = ", ".join(self.config.get("validation_strategies", {}).keys())
        engineer_summary = json.dumps(action_plan_data, ensure_ascii=False, indent=2)

        memory_context_str = ""
        if memory_summary and memory_summary.strip() and memory_summary != "No relevant history available.":
            memory_context_str = f"""
[HISTÓRICO RECENTE (OBJETIVOS E ESTRATÉGIAS USADAS)]
{memory_summary}
Considere este histórico ao tomar sua decisão. Evite repetir estratégias que falharam recentemente para objetivos semelhantes.
"""

        for model in self.model_list:
            self.logger.info(f"MaestroAgent: Tentando com o modelo: {model} para decisão...")

            prompt = f"""
[IDENTIDADE]
Você é o Maestro do agente Hephaestus. Sua tarefa é analisar a proposta do Engenheiro (plano de patches) e o histórico recente para decidir a melhor ação.

[CONTEXTO E HISTÓRICO]
{memory_context_str}

[PROPOSTA DO ENGENHEIRO (PLANO DE PATCHES)]
{engineer_summary}

[SUA DECISÃO]
Com base na proposta e histórico:
1. Se a solução parece razoável e não requer novas capacidades, escolha a estratégia de validação mais adequada.
2. Se a solução requer novas capacidades que Hephaestus precisa desenvolver, responda com `CAPACITATION_REQUIRED`.

Estratégias de Validação Disponíveis: {available_keys}
Opção Adicional: CAPACITATION_REQUIRED

[FORMATO DE SAÍDA OBRIGATÓRIO]
Responda APENAS com um objeto JSON contendo a chave "strategy_key" e o valor sendo UMA das estratégias disponíveis OU "CAPACITATION_REQUIRED".
Exemplo: {{"strategy_key": "sandbox_pytest_validation"}}
Exemplo: {{"strategy_key": "CAPACITATION_REQUIRED"}}
"""
            if self.logger: self.logger.debug(f"MaestroAgent: Prompt para decisão:\n{prompt}")

            attempt_log = {
                "model": model,
                "raw_response": "",
                "parsed_json": None,
                "success": False,
            }

            content, error_api = _call_llm_api(self.api_key, model, prompt, 0.2, self.base_url, self.logger)

            if error_api:
                attempt_log["raw_response"] = f"Erro da API (modelo {model}): {error_api}"
                attempt_logs.append(attempt_log)
                continue

            if not content:
                attempt_log["raw_response"] = f"Resposta de conteúdo vazia da API (modelo {model})"
                attempt_logs.append(attempt_log)
                continue

            attempt_log["raw_response"] = content

            parsed_json, error_parsing = parse_json_response(content, self.logger)

            if error_parsing:
                attempt_log["raw_response"] = f"Erro ao fazer parse (modelo {model}): {error_parsing}. Conteúdo: {content[:200]}"
                attempt_logs.append(attempt_log)
                continue

            if not parsed_json:
                attempt_log["raw_response"] = f"JSON None sem erro de parsing (modelo {model}). Conteúdo: {content[:200]}"
                attempt_logs.append(attempt_log)
                continue

            if not isinstance(parsed_json, dict) or "strategy_key" not in parsed_json:
                error_msg = f"JSON com formato inválido ou faltando 'strategy_key' (modelo {model}). Recebido: {parsed_json}"
                if self.logger: self.logger.warn(f"MaestroAgent: {error_msg}")
                attempt_log["raw_response"] = f"{error_msg}. Original: {content[:200]}"
                attempt_logs.append(attempt_log)
                continue

            attempt_log["parsed_json"] = parsed_json
            attempt_log["success"] = True
            attempt_logs.append(attempt_log)
            break

        return attempt_logs
