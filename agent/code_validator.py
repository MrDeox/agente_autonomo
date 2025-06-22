import tempfile
import os
import py_compile
import sys
import json
import logging # ADICIONADO
from pathlib import Path # ADICIONADO

def validate_python_code(file_path: str | Path, logger: logging.Logger) -> tuple[bool, str | None]:
    """
    Valida se o código Python em um arquivo é sintaticamente correto usando py_compile.
    Retorna (True, None) se válido, ou (False, mensagem de erro) se inválido.
    """
    path_obj = Path(file_path)
    if not path_obj.exists():
        logger.error(f"Arquivo Python não encontrado para validação de sintaxe: {path_obj}")
        return False, f"Arquivo não encontrado: {path_obj}"

    temp_name_c = None # Para o arquivo .pyc, se gerado fora do diretório original
    try:
        # py_compile.compile pode criar um arquivo .pyc.
        # Se não especificarmos cfile, ele pode criar no mesmo diretório ou em __pycache__.
        # Para evitar isso em um ambiente de "apenas leitura" ou para manter limpo,
        # podemos tentar compilar para um .pyc temporário, embora doraise=True
        # deva levantar a exceção antes de escrever muito se houver erro de sintaxe.
        # A maneira mais simples é deixar compilar e, se bem-sucedido, o .pyc pode ser ignorado ou limpo se necessário.
        # Por segurança, vamos compilar para um local de 'nul' ou temporário para o .pyc

        # Determinar um caminho para o arquivo compilado que seja seguro
        # Em alguns sistemas, os.devnull pode não ser um caminho válido para cfile
        # Uma abordagem mais robusta é não especificar cfile e deixar o Python lidar com __pycache__
        # ou compilar com um cfile temporário.
        # Vamos tentar compilar diretamente o arquivo. Se for bem-sucedido, ótimo.
        # O `doraise=True` é o mais importante.
        
        logger.debug(f"Validando sintaxe Python de: {path_obj}")
        py_compile.compile(str(path_obj), doraise=True) # Não especificar cfile, deixar o padrão
        logger.debug(f"Sintaxe Python de '{path_obj}' é válida.")
        return True, None
    
    except py_compile.PyCompileError as e:
        logger.warn(f"Erro de sintaxe Python em '{path_obj}': {e.msg}")
        return False, e.msg # e.msg é geralmente mais limpo que str(e)
    except Exception as e: # Capturar outros erros, como problemas de permissão, etc.
        logger.error(f"Erro inesperado ao validar Python em '{path_obj}': {e}", exc_info=True)
        return False, f"Erro inesperado: {str(e)}"
    finally:
        # Limpeza de .pyc se quisermos ser muito rigorosos, mas geralmente não é necessário
        # para apenas validação de sintaxe com doraise=True.
        # Se py_compile.compile criar um .pyc no mesmo diretório e quisermos limpar:
        # pyc_file = path_obj.with_suffix(".pyc")
        # if pyc_file.exists():
        # try: pyc_file.unlink()
        # except OSError: pass
        pass


def validate_json_syntax(file_path: str | Path, logger: logging.Logger) -> tuple[bool, str | None]:
    """Valida se um arquivo contém JSON válido.
    
    Args:
        file_path: Caminho para o arquivo JSON.
        logger: Instância do logger.
        
    Returns:
        Tupla (is_valid, error_message ou None)
    """
    path_obj = Path(file_path)
    if not path_obj.exists():
        logger.error(f"Arquivo JSON não encontrado para validação de sintaxe: {path_obj}")
        return False, f"Arquivo não encontrado: {path_obj}"

    try:
        logger.debug(f"Validando sintaxe JSON de: {path_obj}")
        with open(path_obj, "r", encoding="utf-8") as f:
            json.load(f) # Tenta carregar o JSON do arquivo
        logger.debug(f"Sintaxe JSON de '{path_obj}' é válida.")
        return True, None
    except json.JSONDecodeError as e:
        logger.warn(f"Erro de sintaxe JSON em '{path_obj}': {e.msg}")
        return False, e.msg # e.msg é geralmente mais limpo
    except Exception as e:
        logger.error(f"Erro inesperado ao validar JSON em '{path_obj}': {e}", exc_info=True)
        return False, f"Erro inesperado: {str(e)}"
