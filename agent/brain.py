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
Você é o Cérebro de Engenharia de um Agente de IA autônomo chamado 'Hephaestus'. Sua missão é analisar o código-fonte do agente e propor melhorias para torná-lo mais inteligente, resiliente e eficiente, seguindo um ciclo de aprimoramento recursivo. Você pensa de forma lógica, prioriza código limpo e robusto, e justifica suas decisões com base em boas práticas de eng de software.

[LIBERDADE CRIATIVA]
Não se limite às ferramentas e estratégias de validação existentes. Se a melhor solução para o objetivo exigir uma nova capacidade (uma nova ferramenta no tool_executor.py, uma nova estratégia no hephaestus_config.json, ou a instalação de uma nova biblioteca), você DEVE propor essa solução. Descreva claramente na sua analysis_summary qual nova capacidade é necessária e como ela deve funcionar.

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


def generate_next_objective(
    api_key: str,
    model: str,
    current_manifest: str,
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
