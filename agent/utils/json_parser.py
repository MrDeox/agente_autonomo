import json
import logging
import traceback
from typing import Optional, Dict, Any, Tuple

def parse_json_response(raw_str: str, logger: logging.Logger) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
        if logger:
            logger.error("parse_json_response: Received empty or whitespace-only string.")
        return None, "String de entrada vazia ou apenas espaços em branco."

    clean_content = raw_str.strip()
    if logger: logger.debug(f"parse_json_response: Raw response before cleaning: {raw_str[:300]}...")

    first_brace = clean_content.find('{')
    last_brace = clean_content.rfind('}')

    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        clean_content = clean_content[first_brace:last_brace+1]
        if logger: logger.debug(f"parse_json_response: Extracted JSON content based on braces: {clean_content[:300]}...")
    else:
        # Attempt to remove markdown code blocks if they exist
        if clean_content.startswith('```json'):
            clean_content = clean_content[7:] # Remove ```json
            if clean_content.endswith('```'):
                clean_content = clean_content[:-3] # Remove ```
        elif clean_content.startswith('```'): # Generic code block
            clean_content = clean_content[3:]
            if clean_content.endswith('```'):
                clean_content = clean_content[:-3]
        clean_content = clean_content.strip() # Strip again after potential markdown removal
        if logger: logger.debug(f"parse_json_response: Content after attempting markdown removal (if any): {clean_content[:300]}...")

    # Remove non-printable characters except for common whitespace like \n, \r, \t
    clean_content = ''.join(char for char in clean_content if ord(char) >= 32 or char in ['\n', '\r', '\t'])
    if logger: logger.debug(f"parse_json_response: Final cleaned content before parsing: {clean_content[:300]}...")

    if not clean_content:
        if logger:
            logger.error("parse_json_response: Content became empty after cleaning.")
        return None, "Conteúdo ficou vazio após limpeza."

    try:
        parsed_json = json.loads(clean_content)
        return parsed_json, None
    except json.JSONDecodeError as e:
        # The duplicated error message lines in the original code are preserved here.
        # This could be a point of cleanup later.
        error_message = f"Erro ao decodificar JSON: {str(e)}. Cleaned content (partial): {clean_content[:500]}"
        if logger: logger.error(f"parse_json_response: {error_message}. Original response (partial): {raw_str[:200]}")
        return None, f"Erro ao decodificar JSON: {str(e)}. Original response (partial): {raw_str[:200]}"
        # This second block is effectively dead code due to the return above, but kept for fidelity to original.
        # error_message = f"Erro ao decodificar JSON: {str(e)}. Conteúdo limpo (parcial): {clean_content[:500]}"
        # if logger:
        #     logger.error(
        #         f"parse_json_response: {error_message}. Resposta original (parcial): {raw_str[:200]}"
        #     )
        # return None, f"Erro ao decodificar JSON: {str(e)}. Resposta original (parcial): {raw_str[:200]}"

    except Exception as e:
        error_message = f"Erro inesperado ao processar JSON: {str(e)}"
        detailed_error = (
            f"{error_message}\n{traceback.format_exc()}" if 'traceback' in globals() else error_message
        )
        if logger:
            logger.error(f"parse_json_response: {detailed_error}", exc_info=True)
        return None, f"Erro inesperado ao processar JSON: {str(e)}"
