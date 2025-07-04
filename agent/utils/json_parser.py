import json
import logging
import re
import traceback
from typing import Optional, Dict, Any, Tuple

def _fix_common_json_errors(json_string: str, logger: logging.Logger) -> str:
    """Tenta corrigir erros comuns de JSON gerado por LLM."""
    # Corrige barras invertidas que não são de escape (causa comum de erro)
    # Ex: "path": "C:\Users\..." se torna "path": "C:\\Users\\..."
    # Usando uma função para a substituição para logar as correções
    def escape_backslashes(match):
        val = match.group(0)
        # Não escapar sequências de escape JSON válidas
        if val in ('\\"', '\\\\', '\\/', '\\b', '\\f', '\\n', '\\r', '\\t'):
            return val
        logger.warning(f"JSON parser: Found potentially unescaped backslash. Correcting '{val}' to '\\{val}'.")
        return f'\\\\{val[1:]}'

    # Regex para encontrar uma barra invertida seguida por um caractere que não é uma sequência de escape válida
    corrected_string = re.sub(r'\\(?![/"\\bfnrt])', escape_backslashes, json_string)
    
    # Tenta corrigir strings não terminadas (caso simples)
    if 'Unterminated string' in corrected_string:
        # Lógica simples: encontrar a última aspa de abertura e adicionar uma no final se necessário
        # Isso é arriscado e pode ser melhorado
        pass
        
    return corrected_string

def parse_json_response(raw_str: str, logger: logging.Logger) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Analisa uma string bruta que se espera conter JSON, limpando-a e decodificando-a.
    Remove blocos de markdown, extrai conteúdo, tenta corrigir erros comuns e carrega o JSON.
    """
    if not raw_str or not raw_str.strip():
        if logger:
            logger.error("parse_json_response: Received empty or whitespace-only string.")
        return None, "String de entrada vazia ou apenas espaços em branco."

    clean_content = raw_str.strip()
    if logger: logger.debug(f"parse_json_response: Raw response before cleaning: {raw_str[:300]}...")

    # Extração primária: do primeiro '{' ao último '}'
    first_brace = clean_content.find('{')
    last_brace = clean_content.rfind('}')
    if first_brace != -1 and last_brace > first_brace:
        clean_content = clean_content[first_brace:last_brace+1]
    else: # Fallback para remover markdown
        if clean_content.startswith('```json'):
            clean_content = clean_content.lstrip('```json').rstrip('```')
        elif clean_content.startswith('```'):
            clean_content = clean_content.lstrip('```').rstrip('```')
    clean_content = clean_content.strip()

    if not clean_content:
        if logger:
            logger.error("parse_json_response: Content became empty after cleaning.")
        return None, "Conteúdo ficou vazio após limpeza."

    # Tentativa 1: Parse direto
    try:
        return json.loads(clean_content), None
    except json.JSONDecodeError as e:
        logger.warning(f"Initial JSON parsing failed: {e}. Attempting to fix common errors.")
        
        # Tentativa 2: Corrigir erros comuns e tentar novamente
        corrected_json_str = _fix_common_json_errors(clean_content, logger)
        try:
            logger.info("Attempting to parse with fixed JSON string...")
            return json.loads(corrected_json_str), None
        except json.JSONDecodeError as e2:
            error_message = f"Erro ao decodificar JSON mesmo após tentativa de correção: {e2}."
            if logger: 
                logger.error(f"parse_json_response: {error_message}. Resposta original (parcial): {raw_str[:200]}")
            return None, error_message
    except Exception as e:
        error_message = f"Erro inesperado ao processar JSON: {str(e)}"
        if logger:
            logger.error(f"parse_json_response: {error_message}", exc_info=True)
        return None, error_message
