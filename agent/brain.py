import json
import requests
import traceback
from typing import Optional, Dict, Any, List, Tuple

def get_ai_suggestion(
    api_key: str,
    model_list: List[str],
    project_snapshot: str,
    objective: str,
    base_url: str = "https://openrouter.ai/api/v1"
) -> List[Dict[str, Any]]:
    """
    Obtém sugestões de LLMs via OpenRouter API usando lista de fallback.
    Retorna uma lista de dicionários com logs detalhados de cada tentativa.
    """
    attempt_logs = []
    
    for model in model_list:
        print(f"Tentando com o modelo: {model}...")
        url = f"{base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""
[CONTEXTO GERAL E IDENTIDADE]
Você é o Cérebro de Engenharia de um Agente de IA autônomo chamado 'Hephaestus'. Sua missão is analisar o código-fonte do agente e propor melhorias para torná-lo mais inteligente, resiliente e eficiente, seguindo um ciclo de aprimoramento recursivo. Você pensa de forma lógica, prioriza código limpo e robusto, e justifica suas decisões com base em boas práticas de eng de software.

[OBJETIVO DA TAREFA ATUAL]
Seu objetivo específico para esta execução é: {objective}

[FORMATO DE SAÍDA OBRIGATÓRIO]
Sua resposta DEVE SER um objeto JSON válido e NADA MAIS. Não inclua explicações, saudações ou qualquer texto fora do objeto JSON. A estrutura do JSON deve ser:
{{
  "analysis_summary": "No campo 'analysis_summary', escreva como um engenheiro sênior reportando para outro, explicando o raciocínio técnico e os benefícios da mudança proposta.",
  "files_to_update": [
    {{
      "file_path": "caminho/do/arquivo.py",
      "new_content": "O código completo e atualizado do arquivo."
    }}
  ],
  "validation_pytest_code": "OPCIONAL: Uma string contendo o código de um novo teste em pytest para validar a mudança proposta. Se a mudança for simples e não necessitar de um novo teste, esta chave pode ser omitida ou o valor ser null/vazio."
}}

[DADOS DE ENTRADA]
Abaixo está o snapshot atual do código do projeto 'Hephaestus' para sua análise:
{project_snapshot}
"""

        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        attempt_log = {
            "model": model,
            "raw_response": "",
            "parsed_json": None,
            "success": False
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            attempt_log["raw_response"] = content
            
            try:
                # Remove possible Markdown code block wrappers
                clean_content = content.strip()
                if clean_content.startswith('```json'):
                    # Extract JSON from code block
                    clean_content = clean_content[7:]  # Remove '```json'
                    if clean_content.endswith('```'):
                        clean_content = clean_content[:-3]
                elif clean_content.startswith('```'):
                    clean_content = clean_content[3:]
                    if clean_content.endswith('```'):
                        clean_content = clean_content[:-3]
                
                parsed = json.loads(clean_content)
                attempt_log["parsed_json"] = parsed
                attempt_log["success"] = True
            except json.JSONDecodeError as e:
                attempt_log["raw_response"] = f"Conteúdo original: {content}\nJSONDecodeError: {str(e)}"
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                error_details = f"Status: {e.response.status_code}, Response: {e.response.text}"
            else:
                error_details = str(e)
            attempt_log["raw_response"] = f"Request failed: {error_details}"
        except KeyError as e:
            attempt_log["raw_response"] = f"KeyError: {str(e)} in API response"
        except Exception as e:
            attempt_log["raw_response"] = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
        
        attempt_logs.append(attempt_log)
    
    return attempt_logs


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
Você é o Maestro do agente Hephaestus. Analise a proposta do Engenheiro abaixo e escolha a estratégia de validação mais adequada.
Estratégias disponíveis: {available_keys}

Proposta do Engenheiro:
{engineer_summary}

Responda apenas com um JSON no formato:
{{"strategy_key": "<UMA_DAS_CHAVES_ACIMA>"}}
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
            content = response.json()["choices"][0]["message"]["content"]
            attempt_log["raw_response"] = content

            clean_content = content.strip()
            if clean_content.startswith('```json'):
                clean_content = clean_content[7:]
                if clean_content.endswith('```'):
                    clean_content = clean_content[:-3]
            elif clean_content.startswith('```'):
                clean_content = clean_content[3:]
                if clean_content.endswith('```'):
                    clean_content = clean_content[:-3]

            parsed = json.loads(clean_content)
            attempt_log["parsed_json"] = parsed
            attempt_log["success"] = True
        except Exception as e:
            attempt_log["raw_response"] = f"Erro na decisão do Maestro: {str(e)}"

        attempt_logs.append(attempt_log)

    return attempt_logs
