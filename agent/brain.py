import json
import requests
import traceback # Mantido para uso potencial em tratamento de erros, embora não usado diretamente nas novas funções.
from typing import Optional, Dict, Any, List, Tuple # Tuple não é usado, mas pode ser mantido por enquanto.

# Funções de comunicação com API (simuladas/reutilizadas)
# Idealmente, haveria uma função genérica para chamadas de API para evitar duplicação.

def _call_llm_api(api_key: str, model: str, prompt: str, temperature: float, base_url: str) -> Tuple[Optional[str], Optional[str]]:
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
        content = response.json()["choices"][0]["message"]["content"]
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
    base_url: str = "https://openrouter.ai/api/v1"
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Fase 2 (Arquiteto): Pega o objetivo e o manifesto, e retorna um plano de ação em JSON.
    Retorna um dicionário com o plano ou None em caso de erro, mais uma mensagem de erro.
    """
    prompt = f"""
Você é o Arquiteto de Software do agente Hephaestus. Sua tarefa é pegar o objetivo de alto nível e, com base no manifesto do projeto, criar um plano de ação detalhado e sequencial.

[OBJETIVO]
{objective}

[MANIFESTO DO PROJETO]
{manifest}

[SUA TAREFA]
Crie um plano JSON com uma lista de operações atômicas. As operações válidas são: 'CREATE_FILE', 'APPEND_TO_FILE', 'REPLACE_BLOCK', 'DELETE_BLOCK'. Para operações em arquivos existentes, você DEVE LER o arquivo antes de planejar.

[FORMATO DE SAÍDA OBRIGATÓRIO]
Sua resposta DEVE ser um objeto JSON válido e nada mais.
{{
  "analysis": "Sua análise e raciocínio para o plano.",
  "action_plan": [
    {{
      "action": "CREATE_FILE",
      "path": "caminho/do/arquivo.py",
      "content_description": "Descrição do conteúdo inicial. Ex: Um arquivo Python com imports básicos."
    }},
    {{
      "action": "APPEND_TO_FILE",
      "path": "caminho/do/arquivo.py",
      "content_description": "Descrição do bloco de código a ser adicionado no final do arquivo."
    }},
    {{
      "action": "REPLACE_BLOCK",
      "path": "caminho/do/arquivo.py",
      "start_line": "<int, número da primeira linha do bloco a ser substituído (base 1)>",
      "end_line": "<int, número da última linha do bloco a ser substituído (base 1)>",
      "content_description": "Descrição do novo bloco de código que substituirá o antigo."
    }}
  ]
}}
"""
    print(f"Gerando plano de ação com o modelo: {model}...")
    raw_response, error = _call_llm_api(api_key, model, prompt, 0.5, base_url) # Temperatura um pouco mais baixa para planejamento

    if error:
        return None, f"Erro ao chamar LLM para plano de ação: {error}"
    if not raw_response:
        return None, "Resposta vazia do LLM para plano de ação."

    try:
        # Remove possible Markdown code block wrappers
        clean_content = raw_response.strip()
        if clean_content.startswith('```json'):
            clean_content = clean_content[7:]
            if clean_content.endswith('```'):
                clean_content = clean_content[:-3]
        elif clean_content.startswith('```'): # Handle cases where ```json is not specified
            clean_content = clean_content[3:]
            if clean_content.endswith('```'):
                clean_content = clean_content[:-3]
        
        parsed_json = json.loads(clean_content)
        # Validação básica da estrutura esperada
        if "action_plan" not in parsed_json or not isinstance(parsed_json["action_plan"], list):
            return None, "JSON do plano de ação não contém a chave 'action_plan' ou não é uma lista."
        return parsed_json, None
    except json.JSONDecodeError as e:
        return None, f"Erro ao decodificar JSON do plano de ação: {str(e)}. Resposta recebida: {raw_response}"
    except Exception as e:
        return None, f"Erro inesperado ao processar plano de ação: {str(e)}"


def generate_code_for_action(
    api_key: str,
    model: str, # Modelo para o Engenheiro de Código
    action: dict,
    file_content: Optional[str],
    base_url: str = "https://openrouter.ai/api/v1"
) -> Tuple[Optional[str], Optional[str]]:
    """
    Fase 3 (Engenheiro de Código): Recebe UMA ÚNICA ação do plano e gera APENAS o código para ela.
    Retorna o código gerado ou None em caso de erro, mais uma mensagem de erro.
    """
    action_description = action.get("content_description", "Nenhuma descrição fornecida para esta ação.")
    
    prompt = f"""
Você é um programador especialista. Sua única tarefa é escrever o bloco de código Python necessário para cumprir a seguinte instrução. Gere APENAS o código, sem explicações ou markdown.

[INSTRUÇÃO]
{action_description}
"""
    if file_content is not None: # Adiciona contexto do arquivo apenas se aplicável
        prompt += f"""
[CONTEXTO DO ARQUIVO (se aplicável)]
```python
{file_content}
```
"""
    else: # Especifica se é um novo arquivo
        if action.get("action") == "CREATE_FILE":
            prompt += "\n[NOTA] Esta é a criação de um NOVO arquivo. Gere o conteúdo completo inicial conforme a instrução."
        else: # Para outras ações que deveriam ter file_content mas não têm (ex: APPEND a arquivo inexistente, erro de lógica)
            prompt += "\n[ALERTA] O conteúdo do arquivo não foi fornecido, mas a ação não é CREATE_FILE. Proceda com base apenas na instrução, mas isso pode ser um erro no plano."


    print(f"Gerando código para a ação '{action.get('action')}' no arquivo '{action.get('path')}' com o modelo: {model}...")
    # Usar temperatura mais baixa para geração de código para ser mais determinístico
    generated_code, error = _call_llm_api(api_key, model, prompt, 0.2, base_url)

    if error:
        return None, f"Erro ao chamar LLM para geração de código: {error}"
    if not generated_code: # Pode ser uma string vazia se o LLM decidir que nada deve ser gerado
        return "", "Resposta vazia do LLM para geração de código (pode ser intencional)."

    # O prompt pede para não incluir markdown, mas por precaução:
    clean_code = generated_code.strip()
    if clean_code.startswith('```python'):
        clean_code = clean_code[9:] # Remove '```python'
        if clean_code.endswith('```'):
            clean_code = clean_code[:-3]
    elif clean_code.startswith('```'): # Handle cases where ```python is not specified but ``` is
        clean_code = clean_code[3:]
        if clean_code.endswith('```'):
            clean_code = clean_code[:-3] # Corrigido para clean_code

    return clean_code, None


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
