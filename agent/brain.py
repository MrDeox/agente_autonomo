import json
import requests
from typing import Optional, Dict, Any

def get_ai_suggestion(
    api_key: str,
    model: str,
    project_snapshot: str,
    objective: str,
    base_url: str = "https://openrouter.ai/api/v1"
) -> Optional[Dict[str, Any]]:
    """
    Obtém sugestões de uma LLM via OpenRouter API com base no snapshot do projeto e objetivo.
    
    Args:
        api_key: Chave da API OpenRouter
        model: Modelo de IA a ser usado (ex: 'anthropic/claude-3-haiku')
        project_snapshot: Snapshot do projeto gerado por generate_project_snapshot
        objective: Objetivo/tarefa para a IA
        base_url: URL base da API (opcional)
    
    Returns:
        Dicionário com a resposta da IA ou None em caso de erro
    """
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = (
        "Você é um assistente que sugere mudanças em projetos Python. "
        "Sua resposta DEVE ser estritamente um objeto JSON válido com as chaves "
        "'analysis_summary' e 'files_to_update'. Nada de texto fora do JSON."\
        "\nEstrutura esperada: {\"analysis_summary\": \"...\", \"files_to_update\": [{\"file_path\": \"...\", \"new_content\": \"...\"}]}"\
        f"\nObjetivo: {objective}"\
        f"\nArquitetura do projeto:\n{project_snapshot}"
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
        content = response.json()["choices"][0]["message"]["content"]
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return None
    except (requests.exceptions.RequestException, KeyError):
        return None
