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
    
    # Corrige strings não terminadas - adiciona aspas de fechamento se necessário
    def fix_unterminated_strings(match):
        content = match.group(1)
        # Se a string não termina com aspas, adiciona
        if not content.endswith('"'):
            logger.warning(f"JSON parser: Found unterminated string, adding closing quote")
            return f'"{content}"'
        return match.group(0)
    
    # Procura por strings que começam com aspas mas podem não terminar
    corrected_string = re.sub(r'"([^"]*(?:\\.[^"]*)*)"?', fix_unterminated_strings, corrected_string)
    
    # Remove vírgulas extras antes de chaves de fechamento
    corrected_string = re.sub(r',(\s*[}\]])', r'\1', corrected_string)
    
    # Corrige arrays e objetos malformados
    corrected_string = re.sub(r'\[\s*,', '[', corrected_string)  # Remove vírgula inicial em arrays
    corrected_string = re.sub(r'{\s*,', '{', corrected_string)   # Remove vírgula inicial em objetos
    
    logger.info(f"JSON parser: Applied fixes to JSON string")
    return corrected_string

def _extract_json_from_response(raw_str: str, logger: logging.Logger) -> str:
    """
    Extract JSON content from various response formats.
    """
    if not raw_str or not raw_str.strip():
        return ""
    
    # Remove markdown code blocks
    if raw_str.startswith('```json'):
        content = raw_str.lstrip('```json').rstrip('```')
    elif raw_str.startswith('```'):
        content = raw_str.lstrip('```').rstrip('```')
    else:
        content = raw_str
    
    # Try to find JSON object with regex
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        return match.group(0)
    
    # If no JSON object found, try to find array
    match = re.search(r'\[.*\]', content, re.DOTALL)
    if match:
        return match.group(0)
    
    # Fallback: return the cleaned content
    return content.strip()

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

    # Extract JSON content
    clean_content = _extract_json_from_response(raw_str, logger)
    
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
            # Attempt 3: More aggressive fixes
            logger.warning(f"Second parsing attempt failed: {e2}. Applying aggressive fixes...")
            
            # Try to fix more complex issues
            aggressive_fixes = corrected_json_str
            
            # Remove any trailing commas
            aggressive_fixes = re.sub(r',(\s*[}\]])', r'\1', aggressive_fixes)
            
            # Try to balance braces and brackets
            open_braces = aggressive_fixes.count('{')
            close_braces = aggressive_fixes.count('}')
            open_brackets = aggressive_fixes.count('[')
            close_brackets = aggressive_fixes.count(']')
            
            # Add missing closing braces/brackets
            if open_braces > close_braces:
                aggressive_fixes += '}' * (open_braces - close_braces)
            if open_brackets > close_brackets:
                aggressive_fixes += ']' * (open_brackets - close_brackets)
            
            try:
                logger.info("Attempting to parse with aggressive fixes...")
                return json.loads(aggressive_fixes), None
            except json.JSONDecodeError as e3:
                error_message = f"Erro ao decodificar JSON mesmo após tentativas de correção: {e3}."
                if logger: 
                    logger.error(f"parse_json_response: {error_message}. Resposta original (parcial): {raw_str[:200]}")
                return None, error_message
    except Exception as e:
        error_message = f"Erro inesperado ao processar JSON: {str(e)}"
        if logger:
            logger.error(f"parse_json_response: {error_message}", exc_info=True)
        return None, error_message
