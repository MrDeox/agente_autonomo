import requests
from typing import Optional

def get_ai_suggestion(
    api_key: str,
    model: str,
    project_snapshot: str,
    objective: str,
    base_url: str = "https://openrouter.ai/api/v1"
) -> str:
    """
    Obtém sugestões de uma LLM via OpenRouter API com base no snapshot do projeto e objetivo.
    
    Args:
        api_key: Chave da API OpenRouter
        model: Modelo de IA a ser usado (ex: 'anthropic/claude-3-haiku')
        project_snapshot: Snapshot do projeto gerado por generate_project_snapshot
        objective: Objetivo/tarefa para a IA
        base_url: URL base da API (opcional)
    
    Returns:
        Resposta da IA como string
    """
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = (
        f"Com base na seguinte arquitetura de projeto, realize o seguinte objetivo.\n"
        f"Objetivo: {objective}\n"
        f"Arquitetura:\n{project_snapshot}\n"
        "Responda apenas com o código modificado ou com a sua análise."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Erro na chamada da API: {str(e)}"
    except KeyError:
        return "Resposta da API em formato inesperado"
