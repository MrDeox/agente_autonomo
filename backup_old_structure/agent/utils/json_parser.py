import json
import logging
import re
import traceback
from typing import Optional, Dict, Any, Tuple

def _fix_common_json_errors(json_string: str, logger: logging.Logger) -> str:
    """Tenta corrigir erros comuns de JSON gerado por LLM."""
    corrected_string = json_string
    
    # Corrige barras invertidas que não são de escape (causa comum de erro)
    # Ex: "path": "C:\Users\..." se torna "path": "C:\\Users\\..."
    # Usando uma função para a substituição para logar as correções
    def escape_backslashes(match):
        val = match.group(0)
        # Não escapar sequências de escape JSON válidas
        if val in ('\\"', '\\\\', '\\/', '\\b', '\\f', '\\n', '\\r', '\\t'):
            return val
        logger.warning(f"JSON parser: Found potentially unescaped backslash. Correcting '{val}' to '\\{val[1:]}'.")
        return f'\\\\{val[1:]}'

    # Regex para encontrar barras invertidas não escapadas
    corrected_string = re.sub(r'\\[^"\\/bfnrt]', escape_backslashes, corrected_string)
    
    # Corrige aspas faltantes em chaves e valores
    # Padrão: {chave: valor} -> {"chave": "valor"}
    def add_quotes_to_keys_and_values(match):
        key = match.group(1)
        value = match.group(2)
        
        # Verifica se a chave já tem aspas
        if not (key.startswith('"') and key.endswith('"')):
            key = f'"{key}"'
        
        # Verifica se o valor já tem aspas (e não é um número, boolean, null)
        if not (value.startswith('"') and value.endswith('"')):
            # Se não é um número, boolean, null, ou array/object, adiciona aspas
            if not (value.lower() in ['true', 'false', 'null'] or 
                   value.replace('.', '').replace('-', '').isdigit() or
                   value.startswith('[') or value.startswith('{')):
                value = f'"{value}"'
        
        return f'{key}: {value}'
    
    # Regex para encontrar pares chave:valor sem aspas
    # Captura chaves e valores que não estão entre aspas
    corrected_string = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*([^,}\]]+)', add_quotes_to_keys_and_values, corrected_string)
    
    # Corrige aspas simples para aspas duplas
    corrected_string = corrected_string.replace("'", '"')
    
    # Remove espaços extras antes de vírgulas e chaves
    corrected_string = re.sub(r'\s+([,}\]])', r'\1', corrected_string)
    
    logger.info(f"JSON parser: Applied fixes to JSON string")
    return corrected_string

def parse_json_response(raw_str: str, logger: logging.Logger) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Analyzes a raw string to find and parse a JSON object, cleaning and fixing it as needed.
    """
    if not raw_str or not raw_str.strip():
        if logger:
            logger.error("parse_json_response: Received empty or whitespace-only string.")
        return None, "String de entrada vazia ou apenas espaços em branco."

    if logger: 
        logger.debug(f"parse_json_response: Raw response before cleaning: {raw_str[:300]}...")

    # Use regex to find the main JSON block. This is more robust.
    # It looks for a string that starts with { and ends with }, accounting for nesting.
    match = re.search(r'\{.*\}', raw_str, re.DOTALL)
    
    if match:
        clean_content = match.group(0)
    else:
        # Fallback for code blocks without a perfect match
        clean_content = raw_str.strip()
        if clean_content.startswith('```json'):
            clean_content = clean_content.lstrip('```json').rstrip('```')
        elif clean_content.startswith('```'):
            clean_content = clean_content.lstrip('```').rstrip('```')
    
    clean_content = clean_content.strip()

    if not clean_content:
        if logger:
            logger.error("parse_json_response: Content became empty after cleaning and extraction.")
        return None, "Conteúdo ficou vazio após limpeza e extração."

    # Attempt to parse the extracted content
    try:
        return json.loads(clean_content), None
    except json.JSONDecodeError as e:
        logger.warning(f"Initial JSON parsing failed: {e}. Attempting to fix common errors.")
        
        # Attempt 2: Fix common errors and retry
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
